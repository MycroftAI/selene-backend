import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import generate_device_login
from selene.data.device import DeviceRepository


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
            response = (
                generate_device_login(device_id, self.cache),
                HTTPStatus.OK
            )
        else:
            response = '', HTTPStatus.NOT_FOUND
        return response

    def _get_pairing_session(self, device_activate: DeviceActivate):
        """Get the pairing session from the cache.

        device_activate must have same state as that stored in the
        pairing session.
        """
        token = str(device_activate.token)
        token_key = 'pairing.token:{}'.format(token)
        pairing = self.cache.get(token_key)
        if pairing:
            pairing = json.loads(pairing)
            if str(device_activate.state) == pairing['state']:
                self.cache.delete(token_key)
                return pairing

    def _activate(self, device_id: str, device_activate: DeviceActivate):
        """Updates the core version, platform and enclosure_version columns"""
        updates = dict(
            platform=str(device_activate.platform),
            enclosure_version=str(device_activate.enclosureVersion),
            core_version=str(device_activate.coreVersion)
        )
        DeviceRepository(self.db).update_device_from_core(device_id, updates)
