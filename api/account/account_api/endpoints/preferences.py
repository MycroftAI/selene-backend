from dataclasses import asdict
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.data.device import AccountPreferences, PreferenceRepository


class PreferencesRequest(Model):
    date_format = StringType(
        required=True,
        choices=['DD/MM/YYYY', 'MM/DD/YYYY']
    )
    measurement_system = StringType(
        required=True,
        choices=['Imperial', 'Metric']
    )
    time_format = StringType(required=True, choices=['12 Hour', '24 Hour'])


class PreferencesEndpoint(SeleneEndpoint):
    def __init__(self):
        super(PreferencesEndpoint, self).__init__()
        self.preferences = None
        self.cache = self.config['SELENE_CACHE']
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)

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
        preference_repository = PreferenceRepository(self.db, self.account.id)
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

        return response_data

    def post(self):
        self._authenticate()
        self._validate_request()
        self._upsert_preferences()
        self.etag_manager.expire_device_setting_etag_by_account_id(self.account.id)
        return '', HTTPStatus.NO_CONTENT

    def patch(self):
        self._authenticate()
        self._validate_request()
        self._upsert_preferences()
        self.etag_manager.expire_device_setting_etag_by_account_id(self.account.id)
        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        self.preferences = PreferencesRequest()
        self.preferences.date_format = self.request.json['dateFormat']
        self.preferences.measurement_system = (
            self.request.json['measurementSystem']
        )
        self.preferences.time_format = self.request.json['timeFormat']
        self.preferences.validate()

    def _upsert_preferences(self):
        preferences_repository = PreferenceRepository(self.db, self.account.id)
        preferences = AccountPreferences(**self.preferences.to_native())
        preferences_repository.upsert(preferences)
