from http import HTTPStatus

from flask import json
from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.device import DefaultsRepository


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
        default_repository = DefaultsRepository(self.db, self.account.id)
        self.defaults = default_repository.get_account_defaults()

    def post(self):
        self._authenticate()
        defaults = self._validate_request()
        self._upsert_defaults(defaults)

        return '', HTTPStatus.NO_CONTENT

    def patch(self):
        self._authenticate()
        defaults = self._validate_request()
        self._upsert_defaults(defaults)

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        request_data = json.loads(self.request.data)
        defaults = DefaultsRequest()
        defaults.city = request_data.get('city')
        defaults.country = request_data.get('country')
        defaults.region = request_data.get('region')
        defaults.timezone = request_data.get('timezone')
        defaults.voice = request_data['voice']
        defaults.wake_word = request_data['wakeWord']
        defaults.validate()

        return defaults

    def _upsert_defaults(self, defaults):
        defaults_repository = DefaultsRepository(self.db, self.account.id)
        defaults_repository.upsert(defaults.to_native())
