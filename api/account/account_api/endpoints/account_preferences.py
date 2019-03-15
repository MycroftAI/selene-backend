from dataclasses import asdict
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import PreferenceRepository
from selene.util.db import get_db_connection


class AccountPreferencesEndpoint(SeleneEndpoint):
    def __init__(self):
        super(AccountPreferencesEndpoint, self).__init__()
        self.preferences = None

    def get(self):
        self._authenticate()
        self._get_preferences()
        if self.preferences is None:
            response_data = ''
            response_code = HTTPStatus.NO_CONTENT
        else:
            response_data = self._build_response()
            response_code = HTTPStatus.OK

        return response_data, response_code

    def _get_preferences(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            preference_repository = PreferenceRepository(db, self.account.id)
            self.preferences = preference_repository.get_account_preferences()

    def _build_response(self):
        response_data = asdict(self.preferences)
        if self.preferences.wake_word is not None:
            response_data['wake_word'] = dict(
                id=self.preferences.wake_word.id,
                name=self.preferences.wake_word.wake_word
            )
        if self.preferences.voice is not None:
            response_data['voice'] = dict(
                id=self.preferences.voice.id,
                name=self.preferences.voice.display_name
            )
        if self.preferences.geography is not None:
            response_data['geography'] = dict(
                id=self.preferences.geography.id,
                name=self.preferences.geography.country
            )

        return response_data
