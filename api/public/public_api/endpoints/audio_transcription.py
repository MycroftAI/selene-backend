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

import json
from binascii import b2a_base64
from http import HTTPStatus
from io import BytesIO
from os import environ
from typing import Optional

import librosa
import numpy
import requests

from selene.api import PublicEndpoint, track_account_activity
from selene.util.log import get_selene_logger

INT_16_MAX = 32767.0
SAMPLE_RATE = 16000

_log = get_selene_logger(__name__)


class AudioTranscriptionEndpoint(PublicEndpoint):
    """Transcribes audio data to text and responds with the result."""

    def post(self):
        """Processes an HTTP Post request."""
        self._authenticate()
        transcription = self._transcribe()
        if transcription is not None:
            track_account_activity(self.db, self.device_id)

        return dict(transcription=transcription), HTTPStatus.OK

    def _transcribe(self) -> Optional[str]:
        """Transcribes the audio in the request to text using a transcription service.

        :returns: None if the transcription failed or the transcription
        """
        audio = self._format_audio_data()
        response = self._call_transcription_api(audio)
        transcription = self._handle_api_response(response)

        return transcription

    def _format_audio_data(self):
        """Convert audio data in request to encoding needed for Assembly API."""
        with BytesIO(self.request.data) as request_audio:
            audio, _ = librosa.load(request_audio, sr=SAMPLE_RATE, mono=True)
            duration = librosa.get_duration(y=audio, sr=SAMPLE_RATE)
            _log.info("duration of audio file is: %s", duration)
        formatted_audio = audio * (INT_16_MAX / max(0.01, numpy.max(numpy.abs(audio))))
        formatted_audio = numpy.clip(formatted_audio, -INT_16_MAX, INT_16_MAX)
        formatted_audio = formatted_audio.astype("int16")

        return formatted_audio

    def _call_transcription_api(self, audio) -> Optional[requests.Response]:
        """Calls the configured audio transcription service API.

        :returns: None if the call fails or the result of the API call
        """
        response = None
        audio_data = b2a_base64(audio, newline=False).decode()
        request_data = json.dumps(dict(audio_data=audio_data))
        request_headers = {
            "authorization": environ["STT_API_KEY"],
            "content-type": "application/json",
        }
        try:
            response = requests.post(
                environ["STT_URL"], headers=request_headers, data=request_data
            )
            response.raise_for_status()
        except requests.ConnectionError:
            _log.exception(
                f"{self.request_id}: Failed to connect to audio transcription service"
            )
        except requests.HTTPError:
            log_message = (
                f"{self.request_id}: API request to transcription service failed"
            )
            response_text = json.loads(response.text)
            error_message = response_text.get("error")
            if error_message is not None:
                log_message += f": {error_message}"
            _log.exception(log_message)

        return response

    def _handle_api_response(
        self, response: Optional[requests.Response]
    ) -> Optional[str]:
        """Interrogates the response from the transcription service API.

        :param response: the transcription service API response
        :return: None if the audio could not be transcribed or the transcription
        """
        transcription = None
        if response is not None:
            response_data = json.loads(response.text)
            if response_data["status"] == "completed":
                transcription = response_data["text"]
            else:
                _log.warning(f"{self.request_id}: audio could not be transcribed")

        return transcription
