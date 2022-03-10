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
"""Data access and manipulation for the tagging.wake_word_file table."""
import hashlib
from collections import defaultdict
from datetime import date
from logging import getLogger
from typing import List

from psycopg2 import IntegrityError

from selene.data.wake_word import WakeWord
from ..entity.wake_word_file import TaggableFile, WakeWordFile
from ..entity.file_location import TaggingFileLocation
from ...repository_base import RepositoryBase

DELETED_STATUS = "deleted"
PENDING_DELETE_STATUS = "pending delete"
UPLOADED_STATUS = "uploaded"
UNIQUE_VIOLATION = "23505"

_log = getLogger(__name__)


def build_tagging_file_name(file_contents):
    """Use a SHA1 hash of the file contents to build the name of the file."""
    audio_file_hash = hashlib.new("sha1")
    audio_file_hash.update(file_contents)
    file_name = f"{audio_file_hash.hexdigest()}.wav"

    return file_name


class WakeWordFileRepository(RepositoryBase):
    """Data access and manipulation for the tagging.wake_word_file table."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def add(self, wake_word_file: WakeWordFile):
        """Adds a row to the wake word file table

        File names are SHA1 hashes of the file content.  It is possible that a hash
        collision occurs.  In this case, alter the file name to be unique.

        :param wake_word_file: a wake word file for machine learning training
        :return None if no collisions or the new file name if collision found
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
        collisions = 0
        new_file_name = None
        while True:
            try:
                self.cursor.insert(db_request)
                break
            except IntegrityError as integrity_err:
                if integrity_err.pgcode == UNIQUE_VIOLATION:
                    new_file_name = self._handle_file_name_collision(
                        wake_word_file.name, collisions
                    )
                    db_request.args.update(file_name=new_file_name)
                    _log.info(
                        "Wake word file name {file_name} exists. Trying "
                        "{new_file_name}".format(
                            file_name=wake_word_file.name, new_file_name=new_file_name
                        )
                    )
                    collisions += 1
                else:
                    _log.exception(f"Insert of file {wake_word_file.name} failed")
                    raise

        return new_file_name

    @staticmethod
    def _handle_file_name_collision(file_name: str, collisions: int):
        """Make the file name unique if the generated hash exists in the database.

        :param file_name: the name of the file that had a collision
        :param collisions: number of collisions encountered
        :return: the new name to try on next insert attempt
        """
        file_name_parts = file_name.split(".")
        if len(file_name_parts) == 2:
            new_name = ".".join(
                [file_name_parts[0], str(collisions), file_name_parts[1]]
            )
        else:
            new_name = ".".join(
                [file_name_parts[0], str(collisions), file_name_parts[2]]
            )

        return new_name

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

    def get_taggable_file(
        self, wake_word: str, tag_count: int, session_id: str
    ) -> TaggableFile:
        """Retrieve a file that needs to be tagged from the database.

        :param wake_word: the wake word being tagged
        :param tag_count: the number of tag types defined in the database
        :param session_id: identifier of the current tagging session
        :return: an object containing the result of the query
        """
        taggable_file = None
        db_request = self._build_db_request(
            sql_file_name="get_taggable_wake_word_file.sql",
            args=dict(wake_word=wake_word, tag_count=tag_count, session_id=session_id),
        )
        result = self.cursor.select_one(db_request)
        if result is not None:
            file_location = TaggingFileLocation(
                server=result["server"], directory=result["directory"]
            )
            taggable_file = TaggableFile(
                id=result["id"],
                name=result["name"],
                location=file_location,
                designations=result["designations"],
                tag=result["tag"],
            )

        return taggable_file

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

    def remove(self, wake_word_file: WakeWordFile):
        """Delete a single wake word file.

        :param wake_word_file: Object representing the wake word file to delete.
        """
        db_request = self._build_db_request(
            sql_file_name="remove_wake_word_file.sql", args=dict(id=wake_word_file.id),
        )
        self.cursor.delete(db_request)
