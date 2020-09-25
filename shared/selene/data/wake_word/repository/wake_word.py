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
"""Data access and manipulation of the wake_word.wake_word table."""
from typing import List

from selene.data.wake_word.entity.wake_word import WakeWord
from selene.data.repository_base import RepositoryBase

PRECISE_ENGINE = "precise"


class WakeWordRepository(RepositoryBase):
    """Data access and manipulation methods for the wake_word.wake_word table."""

    def __init__(self, db):
        super(WakeWordRepository, self).__init__(db, __file__)

    def get_wake_words_for_web(self) -> List[WakeWord]:
        """Get the list of wake words that are presented to the user in the GUI.

        :return list of objects representing the wake words to display
        """
        # TODO: replace list of hardcoded wake words in SQL with references
        wake_words = self._select_all_into_dataclass(
            dataclass=WakeWord, sql_file_name="get_wake_words_for_web.sql"
        )

        return wake_words

    def ensure_wake_word_exists(self, name: str, engine: str) -> WakeWord:
        """Add a wake word to the database if it does not exist.

        :param name: the words that comprise the wake word
        :param engine: identifies the wake word recognizer framework
        :return an object representing the wake word
        """
        wake_word = WakeWord(name=name, engine=engine)
        wake_word.id = self.get_id(wake_word)
        if wake_word.id is None:
            wake_word.id = self.add(wake_word)

        return wake_word

    def get_id(self, wake_word: WakeWord) -> str:
        """Get the ID of the specified wake word.

        :param wake_word: representation of the wake word to query
        :return the UUID of the wake word row or None if wake word does not exist
        """
        db_request = self._build_db_request(
            sql_file_name="get_wake_word_id.sql",
            args=dict(name=wake_word.name, engine=wake_word.engine),
        )
        result = self.cursor.select_one(db_request)

        return None if result is None else result["id"]

    def add(self, wake_word: WakeWord) -> str:
        """Adds a row to the wake_word table

        :return UUID representing the wake word ID
        """
        db_request = self._build_db_request(
            sql_file_name="add_wake_word.sql",
            args=dict(name=wake_word.name, engine=wake_word.engine),
        )
        result = self.cursor.insert_returning(db_request)

        return result["id"]

    def remove(self, wake_word: WakeWord):
        """Delete a wake word from the wake_word table.

        :param wake_word: representation of the the wake word to delete
        """
        db_request = self._build_db_request(
            sql_file_name="remove_wake_word.sql", args=dict(wake_word_id=wake_word.id)
        )
        self.cursor.delete(db_request)
