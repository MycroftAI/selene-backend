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
"""Data access and manipulation for the tagging.wake_word_file_tag table."""
from dataclasses import asdict
from typing import List

from ..entity.file_designation import FileDesignation
from ...repository_base import RepositoryBase


class FileDesignationRepository(RepositoryBase):
    """Data access and manipulation for the tagging.wake_word_file_tag table."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def add(self, file_designation: FileDesignation):
        """Add a tag to a wake word file."""
        db_request = self._build_db_request(
            sql_file_name="add_wake_word_file_designation.sql",
            args=asdict(file_designation),
        )
        self.cursor.insert(db_request)

    def get_from_date(self, wake_word, start_date) -> List[FileDesignation]:
        """Retrieve files with designations for the given wake word and start date."""
        db_request = self._build_db_request(
            sql_file_name="get_designations_from_date.sql",
            args=dict(wake_word=wake_word, start_date=start_date),
        )
        result = self.cursor.select_all(db_request)
        designations = [FileDesignation(**row) for row in result]

        return designations
