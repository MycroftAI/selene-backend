import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType, UUIDType

from selene.api import PublicEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class AddDevice(Model):
    name = StringType(required=True)
    wake_word_id = UUIDType(required=True)
    text_to_speech_id = UUIDType(required=True)


class AccountDeviceEndpoint(PublicEndpoint):
    """Endpoint to add a device to a given account"""

    def __init__(self):
        super(AccountDeviceEndpoint, self).__init__()
        self.device_pairing_time = 86400

    def post(self, account_id):
        payload = json.loads(self.request.data)
        add_device = AddDevice(payload)
        add_device.validate()
        code = self.request.args['code']
        # Checking if there's one pairing session for the pairing code
        pairing_json = self.cache.get('pairing.code:{}'.format(code))
        if pairing_json:
            device_id = self._finish_pairing(account_id, code, add_device, pairing_json)
            response = device_id, HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def _finish_pairing(self, account_id, code, add_device, pairing_json):
        pairing = json.loads(pairing_json)
        # Removing the pairing code from the cache
        self.cache.delete('pairing.code:{}'.format(code))
        # Finishing the pairing process
        device_id = self._pair(
            account_id,
            add_device,
            pairing
        )
        return device_id

    def _pair(self, account_id: str, add_device: AddDevice, pairing: dict):
        """Creates a device and associate it to a pairing session"""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            result = DeviceRepository(db).add_device(
                account_id,
                str(add_device.name),
                str(add_device.wake_word_id),
                str(add_device.text_to_speech_id)
            )
        pairing['uuid'] = result
        self.cache.set_with_expiration(
            'pairing.token:{}'.format(pairing['token']),
            json.dumps(pairing),
            self.device_pairing_time
        )
        return pairing['uuid']
