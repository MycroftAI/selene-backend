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
"""Data access and manipulation for the tagging.tagger table."""
from dataclasses import asdict
from ..entity.tagger import Tagger
from ...repository_base import RepositoryBase


class TaggerRepository(RepositoryBase):
    """Data access and manipulation for the tagging.tagger table."""

    def __init__(self, db):
        super(TaggerRepository, self).__init__(db, __file__)

    def ensure_tagger_exists(self, tagger: Tagger) -> str:
        """Insert an active session in the database if one does not exist

        :param tagger: the entity that is performing tagging operations
        :return: primary key of the inserted database row
        """
        tagger_id = self._get_by_entity(tagger)
        if tagger_id is None:
            tagger_id = self._add(tagger)

        return tagger_id

    def _get_by_entity(self, tagger: Tagger):
        """Check for existing tagger row

        :param tagger: the entity that is performing tagging operations
        :return: the unique identifier representing the entity.
        """
        tagger_id = None
        db_request = self._build_db_request(
            sql_file_name="get_tagger_by_entity.sql", args=asdict(tagger)
        )
        result = self.cursor.select_one(db_request)
        if result is not None:
            tagger_id = result["id"]

        return tagger_id

    def _add(self, tagger: Tagger):
        """Insert a new row into the tagger.tagger table.

        :param tagger: the entity that is performing tagging operations
        :return: the unique identifier representing the entity.
        """
        db_request = self._build_db_request(
            sql_file_name="add_tagger.sql", args=asdict(tagger)
        )
        result = self.cursor.insert_returning(db_request)

        return result["id"]
