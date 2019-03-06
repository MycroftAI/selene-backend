from dataclasses import asdict
from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


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
