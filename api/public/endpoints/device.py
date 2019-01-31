from selene.api import SeleneEndpoint

from selene.api.base_config import get_base_config
from selene.device import get_device_by_id
from selene.util.db import get_db_connection


class DeviceEndpoint(SeleneEndpoint):

    def __init__(self):
        super(SeleneEndpoint, self).__init__()
        self.connection_pool = get_base_config().DB_CONNECTION_POOL

    def get(self, device_id):
        with get_db_connection(self.connection_pool) as db:
            return get_device_by_id(db, device_id)
