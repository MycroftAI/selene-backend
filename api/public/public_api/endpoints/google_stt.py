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
"""Public API endpoint for transcribing audio using Google's STT API"""
import os
from http import HTTPStatus
from io import BytesIO
from time import time
from typing import List

from speech_recognition import (
    AudioData,
    AudioFile,
    Recognizer,
    RequestError,
    UnknownValueError,
)

from selene.api import PublicEndpoint, track_account_activity
from selene.data.account import AccountRepository, OPEN_DATASET
from selene.util.log import get_selene_logger

_log = get_selene_logger(__name__)

SELENE_DATA_DIR = "/opt/selene/data"


class GoogleSTTEndpoint(PublicEndpoint):
    """Endpoint to send a flac audio file with voice and get back a utterance."""

    def __init__(self):
        super().__init__()
        self.recognizer = Recognizer()
        self.account = None
        self.account_shares_data = False

    def post(self):
        """Processes an HTTP Post request."""
        _log.info(f"{self.request_id}: Google STT transcription requested")
        self._authenticate()
        self._get_account()
        self._check_for_open_dataset_agreement()
        request_audio_data = self._extract_audio_from_request()
        transcription = self._call_google_stt(request_audio_data)
        if transcription is not None:
            self._save_transcription(request_audio_data, transcription)
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

        return transcription

    def _save_transcription(self, audio: AudioData, transcription: str):
        """Saves the STT results for tagging.

        Args:
            audio: the audio data sent to Google's STT API
            transcription: the result of the STT transcription
        """
        if self.account_shares_data:
            flac_audio = audio.get_flac_data()
            file_time = time()
            try:
                self._write_open_dataset_file(flac_audio, file_time, file_type="flac")
                self._write_open_dataset_file(
                    transcription.encode(), file_time, file_type="stt"
                )
            except IOError:
                _log.exception("Failed to write transcription to file system")

    def _write_open_dataset_file(self, content: bytes, file_time: time, file_type: str):
        """Writes one of the pair of transcription files.

        Args:
            content: the data to write to the file
            file_time: the time of the transcription
            file_type: the extension of the file
        """
        file_name = f"{self.account.id}_{file_time}.{file_type}"
        file_path = os.path.join(SELENE_DATA_DIR, file_name)
        with open(file_path, "wb") as stt_file:
            stt_file.write(content)
