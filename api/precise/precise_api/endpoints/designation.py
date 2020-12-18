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
"""Precise API endpoint for retrieving file designations.

A designation is a decision made from a set of tags as to what the attributes of a
sample file are.
"""

from collections import defaultdict
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import List

from selene.api import SeleneEndpoint
from selene.data.tagging import (
    FileDesignation,
    FileDesignationRepository,
    Tag,
    TagRepository,
    TagValue,
)


class DesignationEndpoint(SeleneEndpoint):
    """Precise API endpoint for tagging a file.

    The HTTP GET request will select all sample files for a specified wake word that
    have been designated since a specified date.  Optional tag and tag value arguments
    can be used to filter the result set.
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
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        """Build the response from data retrieved from the database.

        :return the response
        """
        designations = self._get_designations()
        response_data = dict()
        for designation in designations:
            tag = self._get_tag(designation)
            tag_value = self._get_tag_value(designation, tag)
            if self._include_in_result(tag, tag_value):
                if tag.name not in response_data:
                    response_data[tag.name] = defaultdict(list)
                file_path = Path(designation.file_directory).joinpath(
                    designation.file_name
                )
                response_data[tag.name][tag_value.value].append(str(file_path))

        return response_data

    def _get_designations(self) -> List[FileDesignation]:
        """Retrieve the designations from the database that meet the criteria."""
        wake_word = self.request.args["wakeWord"].replace("-", " ")
        start_date = datetime.strptime(self.request.args["startDate"], "%Y-%m-%d")
        designation_repo = FileDesignationRepository(self.db)
        designations = designation_repo.get_from_date(wake_word, start_date)

        return designations

    def _include_in_result(self, tag: Tag, tag_value: TagValue) -> bool:
        """Use the tag associated with a file to determine inclusion in results set.

        :param tag: The tag designated to the sample file
        :param tag_value: The value of the tag designated to the sample file.
        :return a boolean value indicating if the file should be included in response.
        """
        requested_tag = self.request.args.get("tag")
        requested_tag_value = self.request.args.get("tagValue")
        if requested_tag is None:
            include = True
        else:
            include = requested_tag == tag.name and (
                requested_tag_value is None or requested_tag_value == tag_value.value
            )

        return include

    def _get_tag(self, designation: FileDesignation) -> Tag:
        """Get the attributes of the tag designated to the file.

        :param designation: Object containing attributes of the designated file.
        :return: The attributes of the tag
        :raises ValueError when the designation tag is not valid.
        """
        for tag in self.tags:
            if tag.id == designation.tag_id:
                return tag

        raise ValueError(f"Tag ID {designation.tag_id} not found")

    @staticmethod
    def _get_tag_value(designation: FileDesignation, tag: Tag):
        """Get the attributes of the tag value designated to the file.

        :param designation: Object containing attributes of the designated file.
        :param tag: The attributes of the tag, which include valid values
        :return: The attributes of the tag value
        :raises ValueError when the designation tag value is not valid.
        """
        for tag_value in tag.values:
            if tag_value.id == designation.tag_value_id:
                return tag_value

        raise ValueError(f"Tag value ID {designation.tag_value_id} not found")
