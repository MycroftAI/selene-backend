import json
from dataclasses import asdict
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class UpdateDevice(Model):
    coreVersion = StringType()
    platform = StringType()
    platform_build = StringType()
    enclosureVersion = StringType()


class DeviceEndpoint(PublicEndpoint):
    """Return the device entity using the device_id"""
    def __init__(self):
        super(DeviceEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device = DeviceRepository(db).get_device_by_id(device_id)
        if device:
            device = asdict(device)
            if 'placement' in device:
                device['description'] = device.pop('placement')
            if 'core_version' in device:
                device['coreVersion'] = device.pop('core_version')
            if 'enclosure_version' in device:
                device['enclosureVersion'] = device.pop('enclosure_version')
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
                payload.get('platform'),
                payload.get('enclosureVersion'),
                payload.get('coreVersion')
            )
        return '', HTTPStatus.OK
