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
"""Data access and manipulation for the tagging.session table."""
from datetime import datetime, timedelta
from ..entity.tagger import Tagger
from ...repository_base import RepositoryBase


class SessionRepository(RepositoryBase):
    """Data access and manipulation for the tagging.session table."""

    def __init__(self, db):
        super(SessionRepository, self).__init__(db, __file__)

    def ensure_session_exists(self, tagger: Tagger):
        """Insert an active session in the database if one does not exist

        :param tagger: the entity that is performing tagging operations
        :return: primary key of the active session
        """
        new_session_id = None
        active_session_id, last_session_tag_ts = self._get_active(tagger)
        if active_session_id is None:
            new_session_id = self.add(tagger)
        else:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            if last_session_tag_ts is not None and last_session_tag_ts < one_hour_ago:
                self._end_session(active_session_id, last_session_tag_ts)
                new_session_id = self.add(tagger)

        return active_session_id or new_session_id

    def add(self, tagger: Tagger, note: str = None):
        """Insert a row into the tagging.session table

        :param tagger: the entity that is performing tagging operations
        :param note: free form text related to the tagging session
        :return: The unique identifier of the inserted row
        """
        db_request = self._build_db_request(
            sql_file_name="add_session.sql", args=dict(note=note, tagger_id=tagger.id)
        )
        result = self.cursor.insert_returning(db_request)

        return result["id"]

    def _get_active(self, tagger: Tagger):
        """Get the active session (i.e. session without and end timestamp).

        :param tagger: the entity that is performing tagging operations
        :return a two item tuple containing the ID of the active session (if there is
            one) and the timestamp of the last tag applied in this session.
        """
        active_session_id = None
        last_session_tag_ts = None

        db_request = self._build_db_request(
            sql_file_name="get_active_session.sql",
            args=dict(entity_id=tagger.entity_id),
        )
        result = self.cursor.select_one(db_request)
        if result is not None:
            active_session_id = result["id"]
            last_session_tag_ts = result["last_tag_ts"]

        return active_session_id, last_session_tag_ts

    def _end_session(self, session_id, end_ts):
        """Update the active timestamp range tagging.session to the current timestamp

        :param session_id: the session to end
        :param end_ts: the date and time the session ended.
        """
        db_request = self._build_db_request(
            sql_file_name="update_session_end_ts",
            args=dict(session_id=session_id, end_ts=end_ts),
        )
        self.cursor.update(db_request)
