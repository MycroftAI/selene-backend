from http import HTTPStatus

from selene.api import PublicEndpoint, device_setting_etag_key
from selene.data.device import SettingRepository


class DeviceSettingEndpoint(PublicEndpoint):
    """Return the device's settings for the API v1 model"""
    def __init__(self):
        super(DeviceSettingEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_setting_etag_key(device_id))
        setting = SettingRepository(self.db).get_device_settings(device_id)
        if setting is not None:
            response = (setting, HTTPStatus.OK)
            self._add_etag(device_setting_etag_key(device_id))
        else:
            response = ('', HTTPStatus.NO_CONTENT)
        return response
