from http import HTTPStatus

from selene.api import PublicEndpoint


class DeviceSkillEndpoint(PublicEndpoint):
    """Return a skill setting using the API v1 format for a given device and version_hash"""
    def __init__(self):
        super(DeviceSkillEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        return '', HTTPStatus.NO_CONTENT
