import json
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType, BooleanType, ListType, ModelType

from selene.api import PublicEndpoint
from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class SkillField(Model):
    name = StringType()
    type = StringType()
    label = StringType()
    hint = StringType()
    placeholder = StringType()
    hide = BooleanType()
    value = StringType()
    option = StringType()


class SkillSection(Model):
    name = StringType(required=True)
    fields = ListType(ModelType(SkillField))


class SkillMetadata(Model):
    sections = ListType(ModelType(SkillSection))


class Skill(Model):
    name = StringType(required=True)
    identifier = StringType(required=True)
    skillMetadata = ModelType(SkillMetadata)


class DeviceSkillsEndpoint(PublicEndpoint):
    """Fetch all skills associated with a given device using the API v1 format"""

    def __init__(self):
        super(DeviceSkillsEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skills = SkillRepository(db).get_skill_settings_by_device_id(device_id)
        response = (skills, HTTPStatus.OK) if skills is not None else ('', HTTPStatus.NO_CONTENT)
        return response

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        skill = Skill(payload)
        skill.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skill_id = SkillRepository(db).add(device_id, payload)
        return {'uuid': skill_id}, HTTPStatus.OK
