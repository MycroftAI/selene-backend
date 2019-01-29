from selene.util.api import SeleneEndpoint
from selene.util.db import get_view_connection
from selene.skill.skill import get_skill_version_by_device_id


class DeviceSkillEndpoint(SeleneEndpoint):

    def __init__(self):
        super(SeleneEndpoint, self).__init__()
        self.db = get_view_connection()

    def get(self, device_id):
        return get_skill_version_by_device_id(self.db, device_id)
