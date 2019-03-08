import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class UpdateDevice(Model):
    coreVersion = StringType(default='unknown')
    platform = StringType(default='unknown')
    platform_build = StringType()
    enclosureVersion = StringType(default='unknown')


class DeviceEndpoint(PublicEndpoint):
    """Return the device entity using the device_id"""
    def __init__(self):
        super(DeviceEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device = DeviceRepository(db).get_device_by_id(device_id)
        if device:
            if 'placement' in device:
                device['description'] = device.pop('placement')
            if 'core_version' in device:
                device['coreVersion'] = device.pop('core_version')
            if 'enclosure_version' in device:
                device['enclosureVersion'] = device.pop('enclosure_version')
            device['user'] = dict(uuid=device['account_id'])
            del device['account_id']
            response = device, HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def patch(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        update_device = UpdateDevice(payload)
        update_device.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            DeviceRepository(db).update_device(
                device_id,
                payload.get('platform') or 'unknown',
                payload.get('enclosureVersion') or 'unknown',
                payload.get('coreVersion') or 'unknown'
            )
        return '', HTTPStatus.OK
