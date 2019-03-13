from dataclasses import asdict
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import PreferenceRepository
from selene.util.db import get_db_connection


class AccountPreferencesEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response()

        return response_data, HTTPStatus.OK

    def _build_response(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            preference_repository = PreferenceRepository(db, self.account.id)
            preferences = preference_repository.get_account_preferences()

        response_data = asdict(preferences)
        if preferences.wake_word is not None:
            response_data['wake_word'] = dict(
                id=preferences.wake_word.id,
                name=preferences.wake_word.wake_word
            )
        if preferences.voice is not None:
            response_data['voice'] = dict(
                id=preferences.voice.id,
                name=preferences.voice.display_name
            )
        if preferences.geography is not None:
            response_data['geography'] = dict(
                id=preferences.geography.id,
                name=preferences.geography.country
            )

        return response_data
