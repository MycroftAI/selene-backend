import hashlib
import json
import uuid

from flask_restful import http_status_message
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache
from selene.util.db import get_db_connection


class DeviceActivateEndpoint(SeleneEndpoint):
    """Endpoint to activate a device and finish the pairing process"""

    ONE_DAY = 86400

    def __init__(self):
        super(DeviceActivateEndpoint, self).__init__()
        self.cache: SeleneCache = self.config.get('SELENE_CACHE')
        self.sha512 = hashlib.sha512()

    def post(self):
        device_activate = json.loads(self.request.data)
        if device_activate:
            pairing = self._get_pairing_session(device_activate)
            if pairing:
                device_activate['uuid'] = pairing['uuid']
                self._activate(
                    pairing['uuid'],
                    device_activate.get('platform', 'unknown'),
                    device_activate.get('enclosure_version', 'unknown'),
                    device_activate.get('core_version', 'unknown')
                )
                return self._generate_login(device_activate['uuid'])
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

    def _activate(self, device_id: str, platform: str, enclosure_version: str, core_version: str):
        """Updates a device in the database with the core version, platform and enclosure_version fields"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            DeviceRepository(db).update_device(device_id, platform, enclosure_version, core_version)

    def _generate_login(self, device_id: str):
        self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        access = self.sha512.hexdigest()
        self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        refresh = self.sha512.hexdigest()
        login = {
            'uuid': device_id,
            'accessToken': access,
            'refreshToken': refresh,
            'expiration': self.ONE_DAY
        }
        login_json = json.dumps(login)
        # Storing device access token for one:
        self.cache.set_with_expiration('device.session:{uuid}'.format(uuid=device_id), login_json, self.ONE_DAY)
        # Storing device refresh token for ever:
        self.cache.set('device.token.refresh:{refresh}'.format(refresh=refresh), login_json)
        return login

    @staticmethod
    def _token_key(token):
        return 'pairing.token:{}'.format(token)
