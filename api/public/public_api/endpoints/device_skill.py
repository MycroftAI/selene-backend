from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class DeviceSkillEndpoint(SeleneEndpoint):
    """Return a skill setting using the API v1 format for a given device and version_hash"""
    def __init__(self):
        super(DeviceSkillEndpoint, self).__init__()

    def get(self, device_id):
        version_hash = self.request.args.get('identifier')
        if version_hash:
            with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
                skill = SkillRepository(db).get_skill_settings_by_device_id_and_version_hash(device_id, version_hash)
            response = (skill, HTTPStatus.OK) if skill is not None else ('', HTTPStatus.NO_CONTENT)
            return response
