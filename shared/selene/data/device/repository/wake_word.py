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

from ..entity.wake_word import WakeWord
from ...repository_base import RepositoryBase


class WakeWordRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(WakeWordRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_wake_words(self):
        db_request = self._build_db_request(
            sql_file_name='get_wake_words.sql',
            args=dict(account_id=self.account_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [WakeWord(**row) for row in db_result]

    def add(self, wake_word: WakeWord):
        """Adds a row to the wake_word table

        :return wake word id
        """
        db_request = self._build_db_request(
            sql_file_name='add_wake_word.sql',
            args=dict(
                setting_name=wake_word.setting_name,
                display_name=wake_word.display_name,
                account_id=self.account_id,
                engine=wake_word.engine,
            )
        )
        result = self.cursor.insert_returning(db_request)

        return result['id']

    def remove(self, wake_word: WakeWord):
        """Delete a wake word from the wake_word table."""
        db_request = self._build_db_request(
            sql_file_name='delete_wake_word.sql',
            args=dict(wake_word_id=wake_word.id)
        )
        self.cursor.delete(db_request)
