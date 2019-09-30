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

from selene.data.device import DeviceRepository, TextToSpeech


def _build_voice():
    return TextToSpeech(
        setting_name='selene_test_voice',
        display_name='Selene Test Voice',
        engine='mimic'
    )


def add_text_to_speech(db):
    voice = _build_voice()
    device_repository = DeviceRepository(db)
    voice.id = device_repository.add_text_to_speech(voice)

    return voice


def remove_text_to_speech(db, voice):
    device_repository = DeviceRepository(db)
    device_repository.remove_text_to_speech(voice.id)
