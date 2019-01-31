from selene.api import SeleneEndpoint

from selene.api.base_config import get_base_config
from selene.skill.repository import get_skill_version_by_device_id
from selene.util.db import get_db_connection


class DeviceSkillEndpoint(SeleneEndpoint):

    def __init__(self):
        super(SeleneEndpoint, self).__init__()
        self.connection_pool = get_base_config().DB_CONNECTION_POOL

    def get(self, device_id):
        with get_db_connection(self.connection_pool) as db:
            return get_skill_version_by_device_id(db, device_id)
