import json
from http import HTTPStatus

from flask import Response
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import StringType, BooleanType, ListType, ModelType

from selene.api import PublicEndpoint
from selene.api.etag import device_skill_etag_key
from selene.data.skill import SkillRepository

global_id_pattern = '^([^\|@]+)\|([^\|]+$)'             # matches <submodule_name>|<branch>
global_id_dirt_pattern = '^@(.*)\|(.*)\|(.*)$'          # matches @<device_id>|<submodule_name>|<branch>
global_id_non_msm_pattern = '^@([^\|]+)\|([^\|]+$)'     # matches @<device_id>|<folder_name>
global_id_any_pattern = '(?:{})|(?:{})|(?:{})'.format(
    global_id_pattern,
    global_id_dirt_pattern,
    global_id_non_msm_pattern
)


class SkillField(Model):
    name = StringType()
    type = StringType()
    label = StringType()
    hint = StringType()
    placeholder = StringType()
    hide = BooleanType()
    value = StringType()
    options = StringType()


class SkillSection(Model):
    name = StringType(required=True)
    fields = ListType(ModelType(SkillField))


class SkillMetadata(Model):
    sections = ListType(ModelType(SkillSection))


class SkillIcon(Model):
    color = StringType()
    icon = StringType()


class Skill(Model):
    name = StringType()
    skill_gid = StringType(regex=global_id_any_pattern)
    skillMetadata = ModelType(SkillMetadata)
    icon_img = StringType()
    icon = ModelType(SkillIcon)
    display_name = StringType()
    color = StringType()
    identifier = StringType()

    def validate_skill_gid(self, data, value):
        if data['skill_gid'] is None and data['identifier'] is None:
            raise ValidationError('skill should have either skill_gid or identifier define')
        return value


class DeviceSkillsEndpoint(PublicEndpoint):
    """Fetch all skills associated with a given device using the API v1 format"""

    def __init__(self):
        super(DeviceSkillsEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        self._validate_etag(device_skill_etag_key(device_id))
        skills = SkillRepository(self.db).get_skill_settings_by_device_id(device_id)

        if skills is not None:
            response = Response(
                json.dumps(skills),
                status=HTTPStatus.OK,
                content_type='application_json'
            )
            self._add_etag(device_skill_etag_key(device_id))
        else:
            response = Response(
                '',
                status=HTTPStatus.NO_CONTENT,
                content_type='application_json'
            )
        return response

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        skill = Skill(payload)
        skill.validate()
        skill_id = SkillRepository(self.db).add(device_id, payload)
        return {'uuid': skill_id}, HTTPStatus.OK
