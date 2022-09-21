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
"""Public API endpoint for official Mycroft-supported audio transcriptions.

When a device is configured to use the Mycroft STT plugin for transcribing audio,
this endpoint will be called to do the transcription anonymously.
"""

from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from io import BytesIO
from typing import Optional

import librosa
from google.cloud import speech

from selene.api import PublicEndpoint, track_account_activity
from selene.data.account import AccountRepository
from selene.data.metric import SttTranscriptionMetric, TranscriptionMetricRepository
from selene.util.log import get_selene_logger

SAMPLE_RATE = 16000

_log = get_selene_logger(__name__)


class AudioTranscriptionEndpoint(PublicEndpoint):
    """Transcribes audio data to text and responds with the result."""

    def __init__(self):
        super().__init__()
        self.audio_duration = Decimal(0.0)
        self.transcription_duration = Decimal(0.0)

    def post(self):
        """Processes an HTTP Post request."""
        self._authenticate()
        transcription = self._transcribe()
        self._add_transcription_metric(transcription)
        if transcription is not None:
            track_account_activity(self.db, self.device_id)

        return dict(transcription=transcription), HTTPStatus.OK

    def _transcribe(self) -> Optional[str]:
        """Transcribes the audio in the request to text using a transcription service.

        :returns: None if the transcription failed or the transcription
        """
        response = self._call_transcription_api()
        transcription = self._get_transcription(response)

        return transcription

    def _call_transcription_api(self) -> Optional[speech.RecognizeResponse]:
        """Calls the configured audio transcription service API.

        :returns: None if the call fails or the result of the API call
        """
        response = None
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=self.request.data)
        config_values = dict(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
        )
        config = speech.RecognitionConfig(**config_values)
        start_timestamp = datetime.now()
        try:
            response = client.recognize(config=config, audio=audio)
        except Exception:
            _log.exception(f"{self.request_id}: Transcription failed.")
        finally:
            end_timestamp = datetime.now()
        transcription_duration = (end_timestamp - start_timestamp).total_seconds()
        self.transcription_duration = Decimal(str(transcription_duration))

        return response

    def _get_transcription(
        self, response: Optional[speech.RecognizeResponse]
    ) -> Optional[str]:
        """Interrogates the response from the transcription service API.

        :param response: the transcription service API response
        :return: None if the audio could not be transcribed or the transcription
        """
        transcription = None
        if response:
            highest_confidence = 0
            for result in response.results:
                for alternative in result.alternatives:
                    if alternative.confidence > highest_confidence:
                        transcription = alternative.transcription

        return transcription

    def _add_transcription_metric(self, transcription: str):
        """Adds metrics for this STT transcription to the database."""
        account_repo = AccountRepository(self.db)
        account = account_repo.get_account_by_device_id(self.device_id)
        transcription_metric = SttTranscriptionMetric(
            account_id=account.id,
            engine="Google Cloud",
            success=transcription is not None,
            audio_duration=Decimal(str(self._determine_audio_duration())),
            transcription_duration=Decimal(str(self.transcription_duration)),
        )
        transcription_metric_repo = TranscriptionMetricRepository(self.db)
        transcription_metric_repo.add(transcription_metric)

    def _determine_audio_duration(self) -> float:
        """Determines the duration of the audio data for the metrics."""
        with BytesIO(self.request.data) as request_audio:
            audio, _ = librosa.load(request_audio, sr=SAMPLE_RATE, mono=True)
            return librosa.get_duration(y=audio, sr=SAMPLE_RATE)
