from selene.setting import get_device_settings

from selene.util.db import get_view_connection

from selene.util.api import SeleneEndpoint


class DeviceSettingEndpoint(SeleneEndpoint):
    def __init__(self):
        super(SeleneEndpoint, self).__init__()
        self.db = get_view_connection()

    def get(self, device_id):
        return get_device_settings(self.db, device_id)
