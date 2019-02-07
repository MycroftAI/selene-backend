from selene.api import SeleneEndpoint
from selene.device.repository.device import get_subscription_type_by_device_id
from selene.util.db import get_db_connection


class DeviceSubscriptionEndpoint(SeleneEndpoint):
    def __init__(self):
        super(DeviceSubscriptionEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return get_subscription_type_by_device_id(db, device_id)
