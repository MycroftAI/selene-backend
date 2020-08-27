# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
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
"""Data access and manipulation methods for the wake_word.wake_word table."""
from data.wake_word.entity.wake_word import WakeWord
from data.repository_base import RepositoryBase

PRECISE_ENGINE = "precise"


class WakeWordRepository(RepositoryBase):
    def __init__(self, db):
        super(WakeWordRepository, self).__init__(db, __file__)

    def get_wake_words_for_web(self):
        """Get the list of wake words that are presented to the user in the GUI."""
        # TODO: replace list of hardcoded wake words in SQL with references
        wake_words = {}
        db_request = self._build_db_request(sql_file_name="get_wake_words_for_web.sql")
        for row in self.cursor.select_all(db_request):
            if row["engine"] == PRECISE_ENGINE or row["name"] not in wake_words:
                wake_words[row["name"]] = WakeWord(**row)

        return wake_words

    def add(self, wake_word: WakeWord):
        """Adds a row to the wake_word table

        :return wake word ID
        """
        db_request = self._build_db_request(
            sql_file_name="add_wake_word.sql",
            args=dict(name=wake_word.name, engine=wake_word.engine),
        )
        result = self.cursor.insert_returning(db_request)
        wake_word.id = result["id"]

        return wake_word

    def remove(self, wake_word: WakeWord):
        """Delete a wake word from the wake_word table."""
        db_request = self._build_db_request(
            sql_file_name="remove_wake_word.sql", args=dict(wake_word_id=wake_word.id)
        )
        self.cursor.delete(db_request)
