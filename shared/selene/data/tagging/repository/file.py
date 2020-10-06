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
from collections import defaultdict
from datetime import date
from typing import List

from selene.data.wake_word import WakeWord
from ..entity.file import WakeWordFile
from ..entity.file_location import TaggingFileLocation
from ...repository_base import RepositoryBase

DELETED_STATUS = "deleted"
PENDING_DELETE_STATUS = "pending delete"
UPLOADED_STATUS = "uploaded"


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
            sql_file_name="get_wake_word_files.sql",
            args=dict(wake_word=wake_word.name, engine=wake_word.engine),
        )
        db_request.sql = db_request.sql.format(
            where_clause="ww.name = %(wake_word)s AND ww.engine = %(engine)s"
        )
        for row in self.cursor.select_all(db_request):
            wake_word_files.append(self._convert_db_row_to_dataclass(row))

        return wake_word_files

    def get_by_submission_date(self, submission_date: date) -> List[WakeWordFile]:
        """Get sample file references based on the submission date.

        :param submission_date: identifies the date the file was submitted.
        :return: list of WakeWordFile objects containing the retrieved row
        """
        wake_word_files = []
        db_request = self._build_db_request(
            sql_file_name="get_wake_word_files.sql",
            args=dict(submission_date=submission_date),
        )
        db_request.sql = db_request.sql.format(
            where_clause="ww.name = %(wake_word)s AND ww.engine = %(engine)s"
        )
        for row in self.cursor.select_all(db_request):
            wake_word_files.append(self._convert_db_row_to_dataclass(row))

        return wake_word_files

    def get_pending_delete(self) -> dict:
        """Get wake word files scheduled to be removed from the file system.

        :return: list of WakeWordFile objects containing the retrieved row
        """
        wake_word_files = defaultdict(list)
        db_request = self._build_db_request(sql_file_name="get_wake_word_files.sql")
        db_request.sql = db_request.sql.format(
            where_clause="wwf.status = 'pending delete'::tagging_file_status_enum"
        )
        for row in self.cursor.select_all(db_request):
            wake_word_files[row["account_id"]].append(
                self._convert_db_row_to_dataclass(row)
            )

        return wake_word_files

    @staticmethod
    def _convert_db_row_to_dataclass(row) -> WakeWordFile:
        row.update(
            wake_word=WakeWord(**row["wake_word"]),
            location=TaggingFileLocation(**row["location"]),
        )
        return WakeWordFile(**row)

    def change_file_location(self, wake_word_file_id: str, file_location_id: str):
        """Change the database representation of the file system location

        :param wake_word_file_id: UUID of the file being moved
        :param file_location_id: UUID of the destination on the file server
        """
        db_request = self._build_db_request(
            sql_file_name="change_file_location.sql",
            args=dict(
                file_location_id=file_location_id, wake_word_file_id=wake_word_file_id
            ),
        )
        self.cursor.update(db_request)

    def change_account_file_status(self, account_id: str, status: str):
        """Change the status of all files for a given account.

        :param account_id: UUID of the affected account
        :param status: new status of the files
        """
        db_request = self._build_db_request(
            sql_file_name="change_account_file_status.sql",
            args=dict(account_id=account_id, status=status),
        )
        self.cursor.update(db_request)

    def change_file_status(self, wake_word_file: WakeWordFile, status: str):
        """Change the status of a single wake word file.

        :param wake_word_file: dataclass instance representing a wake word file
        :param status: new status of the files
        """
        db_request = self._build_db_request(
            sql_file_name="change_file_status.sql",
            args=dict(file_name=wake_word_file.name, status=status),
        )
        self.cursor.update(db_request)

    def remove_by_wake_word(self, wake_word: WakeWord):
        """Delete all files related to a wake word.

        :param wake_word: The wake word used in the delete WHERE clause.
        """
        db_request = self._build_db_request(
            sql_file_name="remove_files_by_wake_word.sql",
            args=dict(wake_word_id=wake_word.id),
        )
        self.cursor.delete(db_request)
