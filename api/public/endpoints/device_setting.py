from selene.api import SeleneEndpoint
from selene.data.device.repository.setting import get_device_settings
from selene.util.db import get_db_connection


class DeviceSettingEndpoint(SeleneEndpoint):
    """Return the device's settings for the API v1 model"""
    def __init__(self):
        super(DeviceSettingEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return get_device_settings(db, device_id)
