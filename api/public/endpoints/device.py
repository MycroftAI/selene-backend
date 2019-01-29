from selene.util.api import SeleneEndpoint
from selene.util.db import get_view_connection
from selene.device import get_device_by_id


class DeviceEndpoint(SeleneEndpoint):

    def __init__(self):
        super(SeleneEndpoint, self).__init__()
        self.db = get_view_connection()

    def get(self, device_id):
        return get_device_by_id(self.db, device_id)
