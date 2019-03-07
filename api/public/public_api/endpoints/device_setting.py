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
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            setting = SettingRepository(db).get_device_settings(device_id)
        response = (setting, HTTPStatus.OK) if setting else ('', HTTPStatus.NO_CONTENT)
        return response
