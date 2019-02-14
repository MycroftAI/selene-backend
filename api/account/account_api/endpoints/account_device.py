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
            name = device['name']
            wake_word_id = device['wake_word_id']
            text_to_speech_id = device['text_to_speech_id']
            code = self.request.args['code']
            # Checking if there's one pairing session for the pairing code
            pairing_json = self.cache.get('pairing.code:{}'.format(code))
            if pairing_json:
                pairing = json.loads(pairing_json)
                # Removing the pairing code from the cache
                self.cache.delete('pairing.code:{}'.format(code))
                # Finishing the pairing process
                self._pair(account_id, name, wake_word_id, text_to_speech_id, pairing)
                return http_status_message(200)
            return http_status_message(204)
        return http_status_message(204)

    @staticmethod
    def _code_key(code):
        return 'pairing.code:{}'.format(code)

    def _pair(self, account_id: str, name: str, wake_word_id: str, text_to_speech_id: str, pairing: dict):
        """Creates a device and associate it to a pairing session"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            result = DeviceRepository(db).add_device(account_id, name, wake_word_id, text_to_speech_id)
            pairing['uuid'] = result['id']
            return self.cache.set_with_expiration(
                'pairing.token:{}'.format(pairing['token']),
                json.dumps(pairing),
                self.device_pairing_time
            )
