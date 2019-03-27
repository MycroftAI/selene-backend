import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType, ModelType, ListType, DateTimeType

from selene.api import PublicEndpoint
from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class SkillManifest(Model):
    name = StringType(default='')
    origin = StringType(default='')
    installation = StringType(default='')
    failure_message = StringType(default='')
    status = StringType(default='')
    beta = StringType(default='')
    installed = DateTimeType()
    updated = DateTimeType()


class SkillJson(Model):
    blacklist = ListType(StringType)
    skills = ListType(ModelType(SkillManifest, required=True))


class DeviceSkillManifest(PublicEndpoint):
    def __init__(self):
        super(DeviceSkillManifest, self).__init__()

    def put(self, device_id):
        payload = json.loads(self.request.data)
        skill_json = SkillJson(payload)
        skill_json.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            SkillRepository(db).update_skills_manifest(device_id, payload['skills'])
        return '', HTTPStatus.OK

