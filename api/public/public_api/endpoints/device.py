import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.api import device_etag_key
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
        self._validate_etag(device_etag_key(device_id))
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            device = DeviceRepository(db).get_device_by_id(device_id)

        if device is not None:
            response_data = dict(
                name=device.name,
                description=device.placement,
                coreVersion=device.core_version,
                enclosureVersion=device.enclosure_version,
                platform=device.platform,
                user=dict(uuid=device.account_id)
            )
            response = response_data, HTTPStatus.OK

            self._add_etag(device_etag_key(device_id))
        else:
            response = '', HTTPStatus.NO_CONTENT

        return response

    def patch(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        update_device = UpdateDevice(payload)
        update_device.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            updates = dict(
                platform=payload.get('platform') or 'unknown',
                enclosure_version=payload.get('enclosureVersion') or 'unknown',
                core_version=payload.get('coreVersion') or 'unknown'
            )
            DeviceRepository(db).update_device_from_core(device_id, updates)
        return '', HTTPStatus.OK
