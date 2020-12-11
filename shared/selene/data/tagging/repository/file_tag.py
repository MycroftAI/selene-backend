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
from collections import defaultdict
from dataclasses import asdict

from ..entity.file_tag import FileTag
from ...repository_base import RepositoryBase


class FileTagRepository(RepositoryBase):
    """Data access and manipulation for the tagging.wake_word_file_tag table."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def add(self, file_tag: FileTag):
        """Add a tag to a wake word file."""
        db_request = self._build_db_request(
            sql_file_name="add_wake_word_file_tag.sql", args=asdict(file_tag)
        )
        self.cursor.insert(db_request)

    def get_designation_candidates(self) -> defaultdict:
        """Retrieve file tags that have not yet been converted to designations."""

        designation_candidates = defaultdict(list)
        db_request = self._build_db_request(
            sql_file_name="get_designation_candidates.sql",
        )
        result = self.cursor.select_all(db_request)
        for row in result:
            file_tag = FileTag(
                file_id=row["wake_word_file_id"],
                session_id=row["session_id"],
                tag_id=row["tag_id"],
                tag_value_id=row["tag_value_id"],
            )
            designation_candidates[row["wake_word"]].append(file_tag)

        return designation_candidates
