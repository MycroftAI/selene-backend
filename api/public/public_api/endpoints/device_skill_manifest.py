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

    def get(self, device_id):
        self._authenticate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skills_manifest = SkillRepository(db).get_skills_manifest(device_id)
        if skills_manifest:
            for skill in skills_manifest:
                installed = skill.get('installed')
                if installed:
                    installed = installed.timestamp()
                    skill['installed'] = installed
                updated = skill.get('updated')
                if updated:
                    updated = updated.timestamp()
                    skill['updated'] = updated
            skills_manifest = {'skills': skills_manifest}
            response = skills_manifest, HTTPStatus.OK
        else:
            response = '', HTTPStatus.NOT_MODIFIED
        return response

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        skill_json = SkillJson(payload)
        skill_json.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            SkillRepository(db).update_skills_manifest(device_id, payload['skills'])
        return '', HTTPStatus.OK
