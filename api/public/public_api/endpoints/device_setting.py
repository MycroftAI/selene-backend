from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.device import SettingRepository
from selene.util.db import get_db_connection


class DeviceSettingEndpoint(PublicEndpoint):
    """Return the device's settings for the API v1 model"""
    def __init__(self):
        super(DeviceSettingEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        etag_key = 'device.setting.etag:{uuid}'.format(uuid=device_id)
        self._validate_etag(etag_key)
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            setting = SettingRepository(db).get_device_settings(device_id)
        if setting is not None:
            response = (setting, HTTPStatus.OK)
            self._add_etag(etag_key)
        else:
            response = ('', HTTPStatus.NO_CONTENT)
        return response
