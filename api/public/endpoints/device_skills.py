from selene.api import SeleneEndpoint

from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class DeviceSkillsEndpoint(SeleneEndpoint):
    """Fetch all skills associated with a given device using the API v1 format"""

    def __init__(self):
        super(DeviceSkillsEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return SkillRepository(db).get_skill_settings_by_device_id(device_id)
