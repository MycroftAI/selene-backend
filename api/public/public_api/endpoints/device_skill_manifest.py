import json
from http import HTTPStatus
from logging import getLogger

from flask import Response
from schematics import Model
from schematics.types import (
    StringType,
    ModelType,
    ListType,
    DateTimeType,
    IntType,
    BooleanType
)

from selene.api import PublicEndpoint
from selene.data.device import DeviceSkillRepository
from selene.data.skill import SkillRepository


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
    skill_gid = StringType()


class SkillJson(Model):
    blacklist = ListType(StringType)
    version = IntType()
    skills = ListType(ModelType(SkillManifest, required=True))


_log = getLogger(__package__)


class DeviceSkillManifestEndpoint(PublicEndpoint):
    _device_skill_repo = None

    def __init__(self):
        super(DeviceSkillManifestEndpoint, self).__init__()

    @property
    def device_skill_repo(self):
        if self._device_skill_repo is None:
            self._device_skill_repo = DeviceSkillRepository(self.db)

        return self._device_skill_repo

    def get(self, device_id):
        self._authenticate()
        skills_manifest = self._build_skill_manifest(device_id)

        if skills_manifest:
            response = Response(
                skills_manifest,
                status=HTTPStatus.OK,
                content_type='application/json'
            )
        else:
            response = '', HTTPStatus.NOT_MODIFIED

        return response

    def _build_skill_manifest(self, device_id):
        device_skills = self.device_skill_repo.get_skills_for_device(device_id)
        skills_manifest = []
        for skill in device_skills:
            response_skill = dict(
                origin=skill.install_method,
                installation=skill.install_status,
                failure_message=skill.install_failure_reason,
                installed=None,
                updated=None,
                skill_gid=skill.skill_gid
            )
            if skill.install_ts is not None:
                response_skill['installed'] = skill.install_ts.timestamp()
            if skill.update_ts is not None:
                response_skill['updated'] = skill.update_ts.timestamp()

            skills_manifest.append(response_skill)
        skills_manifest = {'skills': skills_manifest}

        return json.dumps(skills_manifest)

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        skill_json = SkillJson(payload)
        skill_json.validate()
        SkillRepository(self.db).update_skills_manifest(device_id, payload['skills'])
        return '', HTTPStatus.OK
