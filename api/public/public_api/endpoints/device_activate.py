import hashlib
import json
import uuid
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceActivate(Model):
    token = StringType(required=True)
    state = StringType(required=True)
    platform = StringType(default='unknown')
    core_version = StringType(default='unknown')
    enclosure_version = StringType(default='unknown')


class DeviceActivateEndpoint(PublicEndpoint):
    """Endpoint to activate a device and finish the pairing process"""

    ONE_DAY = 86400

    def __init__(self):
        super(DeviceActivateEndpoint, self).__init__()
        self.sha512 = hashlib.sha512()

    def post(self):
        payload = json.loads(self.request.data)
        device_activate = DeviceActivate(payload)
        if device_activate:
            pairing = self._get_pairing_session(device_activate)
            if pairing:
                device_id = pairing['uuid']
                self._activate(device_id, device_activate)
                response = self._generate_login(device_id), HTTPStatus.OK
            else:
                response = '', HTTPStatus.NO_CONTENT
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def _get_pairing_session(self, device_activate: DeviceActivate):
        """Get the pairing session from the cache if device_activate has the same state that
        the state stored in the pairing session"""
        token = str(device_activate.token)
        pairing = self.cache.get(self._token_key(token))
        if pairing:
            pairing = json.loads(pairing)
            if str(device_activate.state) == pairing['state']:
                self.cache.delete(self._token_key(token))
                return pairing

    def _activate(self, device_id: str, device_activate: DeviceActivate):
        """Updates a device in the database with the core version, platform and enclosure_version fields"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            DeviceRepository(db).update_device(
                device_id,
                str(device_activate.platform),
                str(device_activate.enclosure_version),
                str(device_activate.core_version)
            )

    def _generate_login(self, device_id: str):
        self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        access = self.sha512.hexdigest()
        self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        refresh = self.sha512.hexdigest()
        login = dict(
            uuid=device_id,
            accessToken=access,
            refreshToken=refresh,
            expiration=self.ONE_DAY
        )
        login_json = json.dumps(login)
        # Storing device access token for one:
        self.cache.set_with_expiration(
            'device.token.access:{access}'.format(access=access),
            login_json,
            self.ONE_DAY
        )
        # Storing device refresh token for ever:
        self.cache.set('device.token.refresh:{refresh}'.format(refresh=refresh), login_json)
        return login

    @staticmethod
    def _token_key(token):
        return 'pairing.token:{}'.format(token)
