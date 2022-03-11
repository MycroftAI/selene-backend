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

from ..entity.text_to_speech import TextToSpeech
from ...repository_base import RepositoryBase


class TextToSpeechRepository(RepositoryBase):
    def __init__(self, db):
        super(TextToSpeechRepository, self).__init__(db, __file__)

    def get_voices(self):
        db_request = self._build_db_request(sql_file_name="get_voices.sql")
        db_result = self.cursor.select_all(db_request)

        return [TextToSpeech(**row) for row in db_result]

    def add(self, text_to_speech: TextToSpeech):
        """Adds a row to the text_to_speech table

        :return wake word id
        """
        db_request = self._build_db_request(
            sql_file_name="add_text_to_speech.sql",
            args=dict(
                wake_word=text_to_speech.setting_name,
                account_id=text_to_speech.display_name,
                engine=text_to_speech.engine,
            ),
        )
        result = self.cursor.insert_returning(db_request)

        return result["id"]

    # def remove(self, wake_word: WakeWord):
    #     """Delete a wake word from the wake_word table."""
    #     db_request = self._build_db_request(
    #         sql_file_name='delete_wake_word.sql',
    #         args=dict(wake_word_id=wake_word.id)
    #     )
    #     self.cursor.delete(db_request)
