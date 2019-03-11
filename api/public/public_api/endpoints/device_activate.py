import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import generate_device_login
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceActivate(Model):
    token = StringType(required=True)
    state = StringType(required=True)
    platform = StringType(default='unknown')
    coreVersion = StringType(default='unknown')
    enclosureVersion = StringType(default='unknown')
    platform_build = StringType()


class DeviceActivateEndpoint(PublicEndpoint):
    """Endpoint to activate a device and finish the pairing process"""

    def __init__(self):
        super(DeviceActivateEndpoint, self).__init__()

    def post(self):
        payload = json.loads(self.request.data)
        device_activate = DeviceActivate(payload)
        device_activate.validate()
        pairing = self._get_pairing_session(device_activate)
        if pairing:
            device_id = pairing['uuid']
            self._activate(device_id, device_activate)
            response = generate_device_login(device_id, self.cache), HTTPStatus.OK
        else:
            response = '', HTTPStatus.NOT_FOUND
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
                str(device_activate.enclosureVersion),
                str(device_activate.coreVersion)
            )

    @staticmethod
    def _token_key(token):
        return 'pairing.token:{}'.format(token)
