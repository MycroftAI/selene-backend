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

from selene.data.tagging import WakeWordFileRepository
from selene.data.wake_word import WakeWord, WakeWordRepository


def add_wake_word(db):
    wake_word = WakeWord(name="hey selene", engine="precise")
    wake_word_repository = WakeWordRepository(db)
    wake_word.id = wake_word_repository.add(wake_word)

    return wake_word


def remove_wake_word(db, wake_word):
    file_repository = WakeWordFileRepository(db)
    wake_word_repository = WakeWordRepository(db)
    if wake_word.id is None:
        wake_word.id = wake_word_repository.get_id(wake_word)
    for wake_word_file in file_repository.get_by_wake_word(wake_word):
        file_repository.remove(wake_word_file)
    wake_word_repository.remove(wake_word)
