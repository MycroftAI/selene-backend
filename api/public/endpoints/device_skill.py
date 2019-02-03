from selene.api import SeleneEndpoint

from selene.skill.repository import get_skill_version_by_device_id
from selene.util.db import get_db_connection


class DeviceSkillEndpoint(SeleneEndpoint):

    def __init__(self):
        super(SeleneEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return get_skill_version_by_device_id(db, device_id)
