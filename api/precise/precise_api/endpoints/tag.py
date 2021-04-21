# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Precise API endpoint for tagging a file."""

import getpass
from http import HTTPStatus
from os import environ
from pathlib import Path
from typing import List

from flask import jsonify
from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.tagging import (
    FileTag,
    FileTagRepository,
    SessionRepository,
    Tag,
    TaggableFile,
    Tagger,
    TaggerRepository,
    TagRepository,
    WakeWordFileRepository,
)
from selene.util.ssh import get_remote_file, SshClientConfig


class TagPostRequest(Model):
    """Define the expected arguments to be passed in the POST request."""

    tag_id = StringType(required=True)
    tag_value = StringType(required=True)
    file_name = StringType(required=True)
    session_id = StringType(required=True)


class TagEndpoint(SeleneEndpoint):
    """Precise API endpoint for tagging a file.

    The HTTP GET request will randomly select a type of tag, which will in turn be used
    to retrieve an audio file that requires the tag.  The selected audio file must not
    have been tagged in the last hour.  This will prevent the same files from being
    tagged more times than necessary.  The file will also be copied to local storage
    for a subsequent API call.
    """

    _tags = None

    @property
    def tags(self) -> List[Tag]:
        """Get all the possible tags.

        :return a list of all tags and their values
        """
        if self._tags is None:
            tag_repository = TagRepository(self.db)
            tags = tag_repository.get_all()
            self._tags = sorted(tags, key=lambda tag: tag.priority)

        return self._tags

    def get(self):
        """Handle an HTTP GET request."""
        self._authenticate()
        session_id = self._ensure_session_exists()
        response_data, file_to_tag = self._build_response_data(session_id)
        if response_data:
            self._copy_audio_file(file_to_tag)

        return response_data, HTTPStatus.OK if response_data else HTTPStatus.NO_CONTENT

    def _ensure_session_exists(self):
        """If no session ID is provided in the request, get it from the database."""
        session_id = self.request.args.get("sessionId")
        if session_id is None:
            tagger = self._ensure_tagger_exists()
            session_repository = SessionRepository(self.db)
            session_id = session_repository.ensure_session_exists(tagger)

        return session_id

    def _ensure_tagger_exists(self):
        """Get the tagger attributes for this account."""
        tagger = Tagger(entity_type="account", entity_id=self.account.id)
        tagger_repository = TaggerRepository(self.db)
        tagger.id = tagger_repository.ensure_tagger_exists(tagger)

        return tagger

    def _build_response_data(self, session_id: str):
        """Build the response from data retrieved from the database.

        :param session_id: Identifier of the user's tagging session
        :return the response and the taggable file object
        """
        wake_word = self.request.args["wakeWord"].replace("-", " ")
        file_to_tag = self._get_taggable_file(wake_word, session_id)
        if file_to_tag is None:
            response_data = ""
        else:
            tag = self._select_tag(file_to_tag)
            response_data = dict(
                audioFileId=file_to_tag.id,
                audioFileName=file_to_tag.name,
                sessionId=session_id,
                tagId=tag.id,
                tagInstructions=tag.instructions,
                tagName=(wake_word if tag.name == "wake word" else tag.name).title(),
                tagTitle=tag.title,
                tagValues=tag.values,
            )

        return response_data, file_to_tag

    def _get_taggable_file(self, wake_word: str, session_id: str) -> TaggableFile:
        """Get a file that has still requires some tagging for a specified tag type.

        :param wake_word: the wake word being tagged by the user
        :param session_id: identifier of the user's tagging session
        :return: dataclass instance representing the file to be tagged
        """
        file_repository = WakeWordFileRepository(self.db)
        file_to_tag = file_repository.get_taggable_file(wake_word, session_id)

        return file_to_tag

    def _select_tag(self, file_to_tag: TaggableFile) -> Tag:
        """Determine which tag to return in the response.

        :param file_to_tag: Attributes of the file that will be tagged by the user
        :return: the tag to put in the response
        """
        selected_tag = None
        for tag in self.tags:
            if file_to_tag.designations is None:
                selected_tag = tag
            elif file_to_tag.tag is None:
                if tag.id not in file_to_tag.designations:
                    selected_tag = tag
            else:
                if tag.id == file_to_tag.tag:
                    selected_tag = tag
            if selected_tag is not None:
                break

        return selected_tag or self.tags[0]

    @staticmethod
    def _copy_audio_file(file_to_tag: TaggableFile):
        """Copy the file from the location specified in the database to local storage

        :param file_to_tag: dataclass instance representing the file to be tagged
        """
        local_path = Path(environ["SELENE_DATA_DIR"]).joinpath(file_to_tag.name)
        if not local_path.exists():
            if file_to_tag.location.server == environ["PRECISE_SERVER"]:
                remote_user = "precise"
                ssh_port = environ["PRECISE_SSH_PORT"]
            else:
                remote_user = "mycroft"
                ssh_port = 22
            ssh_config = SshClientConfig(
                local_user=getpass.getuser(),
                remote_server=file_to_tag.location.server,
                remote_user=remote_user,
                ssh_port=ssh_port,
            )
            remote_path = Path(file_to_tag.location.directory).joinpath(
                file_to_tag.name
            )
            get_remote_file(ssh_config, local_path, remote_path)

    def post(self):
        """Process HTTP POST request for an account."""
        self._authenticate()
        self._validate_post_request()
        self._add_tag()

        return jsonify("File tagged successfully"), HTTPStatus.OK

    def _validate_post_request(self):
        """Validate the contents of the request object for a POST request."""
        post_request = TagPostRequest(
            dict(
                session_id=self.request.json.get("sessionId"),
                tag_id=self.request.json.get("tagId"),
                tag_value=self.request.json.get("tagValueId"),
                file_name=self.request.json.get("audioFileId"),
            )
        )
        post_request.validate()

    def _add_tag(self):
        """Add the tagging result to the database."""
        file_tag = FileTag(
            file_id=self.request.json["audioFileId"],
            session_id=self.request.json["sessionId"],
            tag_id=self.request.json["tagId"],
            tag_value_id=self.request.json["tagValueId"],
        )
        file_tag_repository = FileTagRepository(self.db)
        file_tag_repository.add(file_tag)
