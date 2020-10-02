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
"""Data access and manipulation for the wake_word.sample table."""
from ..entity.file_location import TaggingFileLocation
from ...repository_base import RepositoryBase


class TaggingFileLocationRepository(RepositoryBase):
    """Data access and manipulation for the wake_word.sample table."""

    def __init__(self, db):
        super(TaggingFileLocationRepository, self).__init__(db, __file__)

    def ensure_location_exists(
        self, server: str, directory: str
    ) -> TaggingFileLocation:
        """If the file location does not exist in the database, add one.

        :param server: IP address of the server the file resides on
        :param directory: fully qualified directory where the file resides
        """
        file_location = TaggingFileLocation(server=server, directory=str(directory))
        file_location.id = self.get_id(file_location)
        if file_location.id is None:
            file_location.id = self.add(file_location)

        return file_location

    def add(self, file_location: TaggingFileLocation) -> str:
        """Inserts a row on the tagging.file_location table.

        :param file_location: object representing the table row to insert.
        :return: the primary key that was auto-generated as part of the insert.
        """
        db_request = self._build_db_request(
            sql_file_name="add_file_location.sql",
            args=dict(server=file_location.server, directory=file_location.directory),
        )
        result = self.cursor.insert_returning(db_request)

        return result["id"]

    def get_id(self, file_location: TaggingFileLocation) -> str:
        """Get the ID of the specified file location.

        :param file_location: object representing the location of the file.
        :return: the primary key representation of the file.
        """
        db_request = self._build_db_request(
            sql_file_name="get_file_location_id.sql",
            args=dict(server=file_location.server, directory=file_location.directory),
        )
        result = self.cursor.select_one(db_request)

        return None if result is None else result["id"]

    def remove(self, file_location: TaggingFileLocation):
        """Delete a row from the file_location table."""
        db_request = self._build_db_request(
            sql_file_name="remove_file_location.sql", args=dict(id=file_location.id),
        )
        self.cursor.delete(db_request)
