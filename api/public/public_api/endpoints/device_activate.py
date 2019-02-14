import json

from flask_restful import http_status_message
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache
from selene.util.db import get_db_connection


class DeviceActivateEndpoint(SeleneEndpoint):
    """Endpoint to activate a device and finish the pairing process"""

    def __init__(self):
        super(DeviceActivateEndpoint, self).__init__()
        self.cache: SeleneCache = self.config.get('SELENE_CACHE')

    def post(self):
        device_activate = self.request.get_json()
        if device_activate:
            pairing = self._get_pairing_session(device_activate)
            if pairing:
                device_activate['uuid'] = pairing['uuid']
                self._activate(device_activate)
                return http_status_message(200)
            return http_status_message(204)
        return http_status_message(204)

    def _get_pairing_session(self, device_activate: dict):
        """Get the pairing session from the cache if device_activate has the same state that
        the state stored in the pairing session"""
        assert ('token' in device_activate and 'state' in device_activate)
        token = device_activate['token']
        pairing = self.cache.get(self._token_key(token))
        if pairing:
            pairing = json.loads(pairing)
            if device_activate['state'] == pairing['state']:
                self.cache.delete(self._token_key(token))
                return pairing

    def _activate(self, device: dict):
        """Updates a device in the database with the core version, platform and enclosure_version fields"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            DeviceRepository(db).update_device(device)

    @staticmethod
    def _token_key(token):
        return 'pairing.token:{}'.format(token)
