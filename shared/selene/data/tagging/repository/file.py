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
from typing import List

from selene.data.wake_word import WakeWord
from ..entity.file import WakeWordFile
from ..entity.file_location import TaggingFileLocation
from ...repository_base import RepositoryBase


class WakeWordFileRepository(RepositoryBase):
    """Data access and manipulation for the wake_word.sample table."""

    def __init__(self, db):
        super(WakeWordFileRepository, self).__init__(db, __file__)

    def add(self, wake_word_file: WakeWordFile):
        """Adds a row to the wake word file table

        :param wake_word_file: a wake word file for machine learning training
        :return wake word id
        """
        db_request = self._build_db_request(
            sql_file_name="add_wake_word_file.sql",
            args=dict(
                wake_word_id=wake_word_file.wake_word.id,
                file_name=wake_word_file.name,
                origin=wake_word_file.origin,
                submission_date=wake_word_file.submission_date,
                account_id=wake_word_file.account_id,
                file_location_id=wake_word_file.location.id,
            ),
        )
        self.cursor.insert(db_request)

    def get_by_wake_word(self, wake_word: WakeWord) -> List[WakeWordFile]:
        """Get a sample file reference based on the file name.

        :param wake_word: identifies the wake word related to the file.
        :return: WakeWordFile object containing the retrieved row
        """
        wake_word_files = []
        db_request = self._build_db_request(
            sql_file_name="get_files_by_wake_word.sql",
            args=dict(wake_word=wake_word.name, engine=wake_word.engine),
        )
        for row in self.cursor.select_all(db_request):
            file_location = TaggingFileLocation(
                server=row["server"], directory=row["directory"]
            )
            wake_word_file = WakeWordFile(
                wake_word=wake_word,
                name=row["name"],
                origin=row["origin"],
                submission_date=row["submission_date"],
                account_id=row["account_id"],
                location=file_location,
            )
            wake_word_files.append(wake_word_file)

        return wake_word_files

    def remove_by_wake_word(self, wake_word: WakeWord):
        """Delete all files related to a wake word."""
        db_request = self._build_db_request(
            sql_file_name="remove_files_by_wake_word.sql",
            args=dict(wake_word_id=wake_word.id),
        )
        self.cursor.delete(db_request)
