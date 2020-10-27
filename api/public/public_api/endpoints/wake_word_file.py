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

"""Public Device API endpoint for uploading a sample wake word for tagging."""
from datetime import datetime
from http import HTTPStatus
from logging import getLogger
from os import environ
from pathlib import Path

from flask import jsonify
from schematics import Model
from schematics.types import StringType
from schematics.exceptions import DataError

from selene.api import PublicEndpoint
from selene.data.account import Account, AccountRepository
from selene.data.tagging import (
    build_tagging_file_name,
    TaggingFileLocationRepository,
    UPLOADED_STATUS,
    WakeWordFile,
    WakeWordFileRepository,
)
from selene.data.wake_word import WakeWordRepository

LOCAL_IP = "127.0.0.1"

_log = getLogger(__package__)


class UploadRequest(Model):
    """Data class for validating the content of the POST request."""

    wake_word = StringType(required=True)
    engine = StringType(required=True)
    timestamp = StringType(required=True)
    model = StringType(required=True)


class WakeWordFileUpload(PublicEndpoint):
    """Endpoint for submitting and retrieving wake word sample files.

    Samples will be saved to a temporary location on the API host until a daily batch
    job moves them to a permanent one.  Each file will be logged on the sample table
    for their location and classification data.
    """

    _file_location = None
    _wake_word_repository = None
    _wake_word = None

    def __init__(self):
        super(WakeWordFileUpload, self).__init__()
        self.request_data = None

    @property
    def wake_word_repository(self):
        """Lazy instantiation of wake word repository object."""
        if self._wake_word_repository is None:
            self._wake_word_repository = WakeWordRepository(self.db)

        return self._wake_word_repository

    @property
    def wake_word(self):
        """Build and return a WakeWord object."""
        if self._wake_word is None:
            self._wake_word = self.wake_word_repository.ensure_wake_word_exists(
                name=self.request_data["wake_word"].strip(),
                engine=self.request_data["engine"],
            )

        return self._wake_word

    @property
    def file_location(self):
        """Build and return a TaggingFileLocation object."""
        if self._file_location is None:
            data_dir = Path(environ["SELENE_DATA_DIR"])
            wake_word = self.request_data["wake_word"].replace(" ", "-")
            wake_word_dir = data_dir.joinpath("wake-word").joinpath(wake_word)
            wake_word_dir.mkdir(parents=True, exist_ok=True)
            file_location_repository = TaggingFileLocationRepository(self.db)
            self._file_location = file_location_repository.ensure_location_exists(
                server=LOCAL_IP, directory=str(wake_word_dir)
            )

        return self._file_location

    def post(self, device_id):
        """
        Process a HTTP POST request submitting a wake word sample from a device.

        :param device_id: UUID of the device that originated the request.
        :return:  HTTP response indicating status of the request.
        """
        self._authenticate(device_id)
        self._validate_post_request()
        account = self._get_account(device_id)
        file_contents = self.request.files["audio_file"].read()
        hashed_file_name = build_tagging_file_name(file_contents)
        new_file_name = self._add_wake_word_file(account, hashed_file_name)
        if new_file_name is not None:
            hashed_file_name = new_file_name
        self._save_audio_file(hashed_file_name, file_contents)

        return jsonify("Wake word sample uploaded successfully"), HTTPStatus.OK

    def _validate_post_request(self):
        """Load the post request into the validation class and perform validations."""
        upload_request = UploadRequest(
            dict(
                wake_word=self.request.form.get("wake_word"),
                engine=self.request.form.get("engine"),
                timestamp=self.request.form.get("timestamp"),
                model=self.request.form.get("model"),
            )
        )
        upload_request.validate()
        self.request_data = upload_request.to_native()
        if "audio_file" not in self.request.files:
            raise DataError(dict(audio_file="No audio file included in request"))

    def _get_account(self, device_id: str):
        """Use the device ID to find the account.

        :param device_id: The database ID for the device that made this API call
        """
        account_repository = AccountRepository(self.db)
        return account_repository.get_account_by_device_id(device_id)

    def _save_audio_file(self, hashed_file_name: str, file_contents: bytes):
        """Build the file path for the audio file."""
        file_path = Path(self.file_location.directory).joinpath(hashed_file_name)
        with open(file_path, "wb") as audio_file:
            audio_file.write(file_contents)

    def _add_wake_word_file(self, account: Account, hashed_file_name: str):
        """Add the sample to the database for reference and classification.

        :param account: the account from which sample originated
        :param hashed_file_name: name of the audio file saved to file system
        """
        sample = WakeWordFile(
            account_id=account.id,
            location=self.file_location,
            name=hashed_file_name,
            origin="mycroft",
            submission_date=datetime.utcnow().date(),
            wake_word=self.wake_word,
            status=UPLOADED_STATUS,
        )
        file_repository = WakeWordFileRepository(self.db)
        new_file_name = file_repository.add(sample)

        return new_file_name
