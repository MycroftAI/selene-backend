from selene.api import SeleneEndpoint

from selene.device import get_device_by_id
from selene.util.db import get_db_connection


class DeviceEndpoint(SeleneEndpoint):

    def __init__(self):
        super(DeviceEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return get_device_by_id(db, device_id)
