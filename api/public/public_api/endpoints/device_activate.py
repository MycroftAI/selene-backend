"""Endpoint to activate a device and finish the pairing process.

A device will call this endpoint every 10 seconds to determine if the user
has completed the device activation process on home.mycroft.ai.  The account
API will set a Redis entry with the a key of "pairing.token" and a value of
the pairing token generated in the pairing code endpoint.  The device passes
the same token in the request body.  When a match is found, the activation
is complete.
"""
import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import generate_device_login
from selene.data.device import DeviceRepository
from selene.util.cache import DEVICE_PAIRING_TOKEN_KEY


class ActivationRequest(Model):
    token = StringType(required=True)
    state = StringType(required=True)
    platform = StringType(default='unknown')
    coreVersion = StringType(default='unknown')
    enclosureVersion = StringType(default='unknown')
    platform_build = StringType()


class DeviceActivateEndpoint(PublicEndpoint):
    def post(self):
        activation_request = ActivationRequest(self.request.json)
        activation_request.validate()
        pairing = self._get_pairing_session(activation_request)
        if pairing:
            device_id = pairing['uuid']
            self._activate(device_id, activation_request)
            response = (
                generate_device_login(device_id, self.cache),
                HTTPStatus.OK
            )
        else:
            response = '', HTTPStatus.NOT_FOUND
        return response

    def _get_pairing_session(self, activation_request: ActivationRequest):
        """Get the pairing session from the cache.

        device_activate must have same state as that stored in the
        pairing session.
        """
        token = str(activation_request.token)
        token_key = DEVICE_PAIRING_TOKEN_KEY.format(pairing_token=token)
        pairing = self.cache.get(token_key)
        if pairing:
            pairing = json.loads(pairing)
            if str(activation_request.state) == pairing['state']:
                self.cache.delete(token_key)
                return pairing

    def _activate(self, device_id: str, activation_request: ActivationRequest):
        """Updates the core version, platform and enclosure_version columns"""
        updates = dict(
            platform=str(activation_request.platform),
            enclosure_version=str(activation_request.enclosureVersion),
            core_version=str(activation_request.coreVersion)
        )
        DeviceRepository(self.db).update_device_from_core(device_id, updates)
