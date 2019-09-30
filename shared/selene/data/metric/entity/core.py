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

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CoreMetric(object):
    device_id: str
    metric_type: str
    metric_value: dict
    id: str = None


@dataclass
class CoreInteraction(object):
    core_id: str
    device_id: str
    start_ts: datetime
    stt_engine: str = None
    stt_transcription: str = None
    stt_duration: Decimal = None
    intent_type: str = None
    intent_duration: Decimal = None
    fallback_handler_duration: Decimal = None
    skill_handler: str = None
    skill_duration: Decimal = None
    tts_engine: str = None
    tts_utterance: str = None
    tts_duration: str = None
    speech_playback_duration: Decimal = None
    user_latency: Decimal = None
    id: str = None
