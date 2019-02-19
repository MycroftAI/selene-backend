from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository

from selene.util.db import get_db_connection


class DeviceEndpoint(SeleneEndpoint):
    """Return the device entity using the device_id"""
    def __init__(self):
        super(DeviceEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return DeviceRepository(db).get_device_by_id(device_id)
