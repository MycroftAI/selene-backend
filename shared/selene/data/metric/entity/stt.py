#  Mycroft Server - Backend
#  Copyright (c) 2022 Mycroft AI Inc
#  SPDX-License-Identifier: 	AGPL-3.0-or-later
#  #
#  This file is part of the Mycroft Server.
#  #
#  The Mycroft Server is free software: you can redistribute it and/or
#  modify it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#  #
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Defines data entities for STT metrics."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class SttTranscriptionMetric:
    """Defines the entity representing the metric.stt_transcription table."""

    account_id: str
    engine: str
    success: bool
    audio_duration: Decimal
    transcription_duration: Decimal


@dataclass
class SttEngineMetric:
    """Defines the entity representing the metric.stt_engine table."""

    activity_dt: date
    engine: str
    requests: int
    success_rate: bool
    transcription_speed: Decimal
    audio_duration: Decimal
    transcription_duration: Decimal
