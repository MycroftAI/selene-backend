from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.api.etag import device_location_etag_key
from selene.data.device import GeographyRepository


class DeviceLocationEndpoint(PublicEndpoint):

    def __init__(self):
        super(DeviceLocationEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_location_etag_key(device_id))
        location = GeographyRepository(self.db, None).get_location_by_device_id(device_id)
        if location:
            response = (location, HTTPStatus.OK)
            self._add_etag(device_location_etag_key(device_id))
        else:
            response = ('', HTTPStatus.NOT_FOUND)
        return response
