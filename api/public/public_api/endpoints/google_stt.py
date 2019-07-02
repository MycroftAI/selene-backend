import os
from http import HTTPStatus
from io import BytesIO
from time import time

from speech_recognition import AudioFile, Recognizer

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository, OPEN_DATASET

SELENE_DATA_DIR = '/opt/selene/data'


class GoogleSTTEndpoint(PublicEndpoint):
    """Endpoint to send a flac audio file with voice and get back a utterance"""
    def __init__(self):
        super(GoogleSTTEndpoint, self).__init__()
        self.google_stt_key = self.config['GOOGLE_STT_KEY']
        self.recognizer = Recognizer()
        self.account = None
        self.account_shares_data = False

    def post(self):
        self._authenticate()
        self._get_account()
        self._check_for_open_dataset_agreement()
        self._write_flac_audio_file()
        stt_response = self._call_google_stt()
        response = self._build_response(stt_response)
        self._write_stt_result_file(response)

        return response, HTTPStatus.OK

    def _get_account(self):
        if self.device_id is not None:
            account_repo = AccountRepository(self.db)
            self.account = account_repo.get_account_by_device_id(self.device_id)

    def _check_for_open_dataset_agreement(self):
        for agreement in self.account.agreements:
            if agreement.type == OPEN_DATASET:
                self.account_shares_data = True

    def _write_flac_audio_file(self):
        """Save the audio file for STT tagging"""
        self._write_open_dataset_file(self.request.data, file_type='.flac')

    def _write_stt_result_file(self, stt_result):
        """Save the STT results for tagging."""
        file_contents = '\n'.join(stt_result)
        self._write_open_dataset_file(file_contents.encode(), file_type='.stt')

    def _write_open_dataset_file(self, content, file_type):
        if self.account is not None:
            file_name = '{account_id}_{time}.{file_type}'.format(
                account_id=self.account.id,
                file_type=file_type,
                time=time()
            )
            file_path = os.path.join(SELENE_DATA_DIR, file_name)
            with open(file_path, 'wb') as flac_file:
                flac_file.write(content)

    def _call_google_stt(self):
        """Use the audio data from the request to call the Google STT API

        We need to replicate the first 16 bytes in the audio due a bug with
        the Google speech recognition library that removes the first 16 bytes
        from the flac file we are sending.
        """
        lang = self.request.args['lang']
        audio = self.request.data
        with AudioFile(BytesIO(audio[:16] + audio)) as source:
            recording = self.recognizer.record(source)
        response = self.recognizer.recognize_google(
            recording,
            key=self.google_stt_key,
            language=lang,
            show_all=True
        )

        return response

    def _build_response(self, stt_response):
        """Build the response to return to the device.

        Return n transcripts with the higher confidence. That is useful for
        the case when send a ambiguous voice file and the correct utterance is
        not the utterance with highest confidence and the API.
        """
        limit = int(self.request.args['limit'])
        if isinstance(stt_response, dict):
            alternative = stt_response.get("alternative")
            if 'confidence' in alternative:
                # Sorting by confidence:
                alternative = sorted(
                    alternative,
                    key=lambda alt: alt['confidence'],
                    reverse=True
                )
                alternative = [alt['transcript'] for alt in alternative]
                # client is interested in test the utterances found.
                if len(alternative) <= limit:
                    response = alternative
                else:
                    response = alternative[:limit]
            else:
                response = [alternative[0]['transcript']]
        else:
            response = []

        return response
