from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.device import GeographyRepository
from selene.util.db import get_db_connection


class DeviceLocationEndpoint(PublicEndpoint):

    def __init__(self):
        super(DeviceLocationEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            location = GeographyRepository(db, None).get_location_by_device_id(device_id)
        response = (location, HTTPStatus.OK) if location else ('', HTTPStatus.NOT_FOUND)
        return response
