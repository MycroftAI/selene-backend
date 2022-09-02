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
"""Public API endpoint for transcribing audio using Google's STT API

DEPRECATION WARNING:
    This endpoint is being replaced with the audio_transcription endpoint.  It will
    remain in the V1 API for backwards compatibility.
"""
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from io import BytesIO

import librosa
from speech_recognition import (
    AudioData,
    AudioFile,
    Recognizer,
    RequestError,
    UnknownValueError,
)

from selene.api import PublicEndpoint, track_account_activity
from selene.data.account import AccountRepository, OPEN_DATASET
from selene.data.metric import SttTranscriptionMetric, TranscriptionMetricRepository
from selene.util.log import get_selene_logger

_log = get_selene_logger(__name__)

SAMPLE_RATE = 16000
SELENE_DATA_DIR = "/opt/selene/data"


class GoogleSTTEndpoint(PublicEndpoint):
    """Endpoint to send a flac audio file with voice and get back a utterance."""

    def __init__(self):
        super().__init__()
        self.recognizer = Recognizer()
        self.account = None
        self.account_shares_data = False
        self.transcription_success = False
        self.audio_duration = 0
        self.transcription_duration = 0

    def post(self):
        """Processes an HTTP Post request."""
        _log.info(f"{self.request_id}: Google STT transcription requested")
        self._authenticate()
        self._get_account()
        self._check_for_open_dataset_agreement()
        request_audio_data = self._extract_audio_from_request()
        transcription = self._call_google_stt(request_audio_data)
        self._add_transcription_metric()
        if transcription is not None:
            track_account_activity(self.db, self.device_id)

        return [transcription], HTTPStatus.OK

    def _get_account(self):
        """Retrieves the account associated with the device from the database."""
        account_repo = AccountRepository(self.db)
        self.account = account_repo.get_account_by_device_id(self.device_id)

    def _check_for_open_dataset_agreement(self):
        """Determines if the account is opted into the Open Dataset Agreement."""
        if self.account is not None:
            for agreement in self.account.agreements:
                if agreement.type == OPEN_DATASET:
                    self.account_shares_data = True
                    break

    def _extract_audio_from_request(self) -> AudioData:
        """Extracts the audio data from the request for use in Google STT API.

        We need to replicate the first 16 bytes in the audio due a bug with
        the Google speech recognition library that removes the first 16 bytes
        from the flac file we are sending.

        Returns:
            Object representing the audio data in a format that can be used to call
            Google's STT API
        """
        _log.info(f"{self.request_id}: Extracting audio data from request")
        request_audio = self.request.data[:16] + self.request.data
        with AudioFile(BytesIO(request_audio)) as source:
            audio_data = self.recognizer.record(source)

        with BytesIO(self.request.data) as request_audio:
            audio, _ = librosa.load(request_audio, sr=SAMPLE_RATE, mono=True)
            self.audio_duration = librosa.get_duration(y=audio, sr=SAMPLE_RATE)

        return audio_data

    def _call_google_stt(self, audio: AudioData) -> str:
        """Uses the audio data from the request to call the Google STT API

        Args:
            audio: audio data representing the words spoken by the user

        Returns:
            text transcription of the audio data
        """
        _log.info(f"{self.request_id}: Transcribing audio with Google STT")
        lang = self.request.args["lang"]
        transcription = None
        start_time = datetime.now()
        try:
            transcription = self.recognizer.recognize_google(
                audio, key=self.config["GOOGLE_STT_KEY"], language=lang
            )
        except RequestError:
            _log.exception("Request to Google TTS failed")
        except UnknownValueError:
            _log.exception("TTS transcription deemed unintelligible by Google")
        else:
            log_message = "Google STT request successful"
            if self.account_shares_data:
                log_message += f": {transcription}"
            _log.info(log_message)
            self.transcription_success = True
        end_time = datetime.now()
        self.transcription_duration = (end_time - start_time).total_seconds()

        return transcription

    def _add_transcription_metric(self):
        """Adds metrics for this STT transcription to the database."""
        account_repo = AccountRepository(self.db)
        account = account_repo.get_account_by_device_id(self.device_id)
        transcription_metric = SttTranscriptionMetric(
            account_id=account.id,
            engine="Google",
            success=self.transcription_success,
            audio_duration=Decimal(str(self.audio_duration)),
            transcription_duration=Decimal(str(self.transcription_duration)),
        )
        transcription_metric_repo = TranscriptionMetricRepository(self.db)
        transcription_metric_repo.add(transcription_metric)
