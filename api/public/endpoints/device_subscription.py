from selene.api import SeleneEndpoint
from selene.data.device.repository.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceSubscriptionEndpoint(SeleneEndpoint):
    def __init__(self):
        super(DeviceSubscriptionEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return DeviceRepository(db).get_subscription_type_by_device_id(device_id)
