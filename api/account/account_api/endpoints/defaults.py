from http import HTTPStatus

from flask import json
from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.device import DefaultsRepository
from selene.util.db import get_db_connection


class DefaultsRequest(Model):
    city = StringType()
    country = StringType()
    region = StringType()
    timezone = StringType()
    voice = StringType()
    wake_word = StringType()


class AccountDefaultsEndpoint(SeleneEndpoint):
    def __init__(self):
        super(AccountDefaultsEndpoint, self).__init__()
        self.defaults = None

    def get(self):
        self._authenticate()
        self._get_defaults()
        if self.defaults is None:
            response_data = ''
            response_code = HTTPStatus.NO_CONTENT
        else:
            response_data = self.defaults
            response_code = HTTPStatus.OK

        return response_data, response_code

    def _get_defaults(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            default_repository = DefaultsRepository(db, self.account.id)
            self.defaults = default_repository.get_account_defaults()

    def post(self):
        self._authenticate()
        defaults = self._validate_request()
        self._add_defaults(defaults)

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        request_data = json.loads(self.request.data)
        preferences = DefaultsRequest()
        preferences.city = request_data.get('city')
        preferences.country = request_data.get('country')
        preferences.region = request_data.get('region')
        preferences.timezone = request_data.get('timezone')
        preferences.voice = request_data['voice']
        preferences.wake_word = request_data['wakeWord']
        preferences.validate()

        return preferences

    def _add_defaults(self, preferences):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            defaults_repository = DefaultsRepository(db, self.account.id)
            defaults_repository.add(preferences.to_native())
