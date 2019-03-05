from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import TextToSpeechRepository
from selene.util.db import get_db_connection


class VoiceEndpoint(SeleneEndpoint):
    def get(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            tts_repository = TextToSpeechRepository(db)
            voices = tts_repository.get_voices()

        response_data = []
        for voice in voices:
            response_data.append(
                dict(id=voice.id, name=voice.display_name, user_defined=False)
            )

        return response_data, HTTPStatus.OK
