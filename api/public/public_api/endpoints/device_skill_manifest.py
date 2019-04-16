import json
from http import HTTPStatus
from logging import getLogger

from flask import Response
from schematics import Model
from schematics.types import StringType, ModelType, ListType, DateTimeType, IntType, BooleanType

from selene.api import PublicEndpoint
from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class SkillManifest(Model):
    name = StringType(required=True)
    origin = StringType(default='')
    installation = StringType(default='')
    failure_message = StringType(default='')
    status = StringType(default='')
    beta = BooleanType(default='')
    installed = DateTimeType()
    updated = DateTimeType()
    update = DateTimeType()


class SkillJson(Model):
    blacklist = ListType(StringType)
    version = IntType()
    skills = ListType(ModelType(SkillManifest, required=True))


_log = getLogger(__package__)


class DeviceSkillManifestEndpoint(PublicEndpoint):
    def __init__(self):
        super(DeviceSkillManifestEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skills_manifest = SkillRepository(db).get_skills_manifest(device_id)
        if skills_manifest:
            for skill in skills_manifest:
                self._convert_to_timestamp(skill)
            skills_manifest = {'skills': skills_manifest}
            skills_manifest = json.dumps(skills_manifest)
            response = Response(skills_manifest, status=HTTPStatus.OK, content_type='application/json')
        else:
            response = '', HTTPStatus.NOT_MODIFIED
        return response

    def _convert_to_timestamp(self, skill):
        installed = skill.get('installed')
        if installed and installed != 0:
            installed = installed.timestamp()
            skill['installed'] = installed
        updated = skill.get('updated')
        if updated and updated != 0:
            updated = updated.timestamp()
            skill['updated'] = updated

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        skill_json = SkillJson(payload)
        skill_json.validate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            SkillRepository(db).update_skills_manifest(device_id, payload['skills'])
        return '', HTTPStatus.OK
