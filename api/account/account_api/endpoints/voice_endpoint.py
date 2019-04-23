from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import TextToSpeechRepository


class VoiceEndpoint(SeleneEndpoint):
    def get(self):
        tts_repository = TextToSpeechRepository(self.db)
        voices = tts_repository.get_voices()

        response_data = []
        for voice in voices:
            response_data.append(
                dict(id=voice.id, name=voice.display_name, user_defined=False)
            )

        return response_data, HTTPStatus.OK
