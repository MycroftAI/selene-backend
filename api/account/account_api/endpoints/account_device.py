import json

from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection
from selene.util.cache import SeleneCache
from flask_restful import http_status_message


class AccountDeviceEndpoint(SeleneEndpoint):
    """Endpoint to add a device to a given account"""

    def __init__(self):
        super(AccountDeviceEndpoint, self).__init__()
        self.cache: SeleneCache = self.config['SELENE_CACHE']
        self.device_pairing_time = 86400

    def post(self, account_id):
        device = self.request.get_json()
        if json:
            name = device.get('name')
            code = self.request.args['code']
            # Checking if there's a pairing session for the pairing code
            pairing_json = self.cache.get(self._code_key(code))
            if pairing_json:
                pairing = json.loads(pairing_json)
                # Removing the pairing code from the cache
                self.cache.delete(self._code_key(code))
                self._pair(account_id, name, pairing)
                return http_status_message(200)
            return http_status_message(204)
        return http_status_message(204)

    @staticmethod
    def _code_key(code):
        return 'pairing.code:{}'.format(code)

    @staticmethod
    def _token_key(token):
        return 'pairing.token:{}'.format(token)

    def _pair(self, account_id: str, name: str, pairing: dict):
        """Creates a device and associate it to a pairing session"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            result = DeviceRepository(db).add_device(account_id, name)
            pairing['uuid'] = result['id']
            return self.cache.set_with_expiration(self._token_key(pairing['token']),
                                                  json.dumps(pairing),
                                                  self.device_pairing_time)
