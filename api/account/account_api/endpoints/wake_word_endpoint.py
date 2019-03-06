from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import WakeWordRepository
from selene.util.db import get_db_connection


class WakeWordEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            wake_word_repository = WakeWordRepository(db, self.account.id)
            wake_words = wake_word_repository.get_wake_words()

        response_data = []
        for wake_word in wake_words:
            response_data.append(
                dict(
                    id=wake_word.id,
                    name=wake_word.wake_word,
                    user_defined=wake_word.user_defined
                )
            )

        return response_data
