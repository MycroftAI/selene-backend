"""Applies a skill settings definition to the database.

Whenever a change is made to a skill's settings definition on a device, the
updated definition is sent to the backend.

This endpoint assumes that the skill manifest is sent when the a device is
paired or a skill is installed. A skill that is not installed on a device
cannot send it's settings... right?  The skill and its relationship to the
device should already be known when this endpoint is called.
"""
from logging import getLogger
from schematics import Model
from schematics.types import (
    BooleanType,
    ListType,
    ModelType,
    StringType
)
from schematics.exceptions import DataError

from selene.api import PublicEndpoint
from selene.data.device import DeviceSkillRepository
from selene.data.skill import (
    SettingsDisplayRepository,
    SkillRepository
)

_log = getLogger(__package__)


def _normalize_field_value(field):
    normalized_value = field.get('value')
    if field['type'].lower() == 'checkbox':
        if field['value'] in ('false', 'False', '0'):
            normalized_value = False
        elif field['value'] in ('true', 'True', '1'):
            normalized_value = True
    elif field['type'].lower() == 'number' and isinstance(field['value'], str):
        normalized_value = float(field['value'])
        if not normalized_value % 1:
            normalized_value = int(field['value'])

    return normalized_value


class RequestSkillField(Model):
    name = StringType()
    type = StringType()
    label = StringType()
    hint = StringType()
    placeholder = StringType()
    hide = BooleanType()
    value = StringType()
    options = StringType()


class RequestSkillSection(Model):
    name = StringType(required=True)
    fields = ListType(ModelType(RequestSkillField))


class RequestSkillMetadata(Model):
    sections = ListType(ModelType(RequestSkillSection))


class RequestSkillIcon(Model):
    color = StringType()
    icon = StringType()


class RequestDeviceSkill(Model):
    display_name = StringType(required=True)
    icon = ModelType(RequestSkillIcon)
    icon_img = StringType()
    name = StringType()
    skill_gid = StringType(required=True)
    skillMetadata = ModelType(RequestSkillMetadata)


class SkillSettingsMetaEndpoint(PublicEndpoint):
    def __init__(self):
        super().__init__()
        self.skill = None
        self.default_settings = None
        self.skill_has_settings = False
        self.settings_definition_id = None

    def put(self, device_id):
        self._authenticate(device_id)
        self._validate_request()
        self._get_skill()
        self._parse_skill_metadata()
        self._update_skill_settings_definition()
        self._get_skill_settings_definition()
        self._update_device_skill(device_id)

    def _validate_request(self):
        request_model = RequestDeviceSkill(**self.request.json)
        request_model.validate()

    def _get_skill(self):
        skill_repo = SkillRepository(self.db)
        self.skill = skill_repo.get_skill_by_global_id(
            self.request.json['skill_gid']
        )
        if self.skill is None:
            err_msg = (
                'No skill on database for skill ' +
                self.request.json['skill_gid']
            )
            _log.error(err_msg)
            raise DataError(err_msg)

    def _parse_skill_metadata(self):
        self.skill_has_settings = 'skillMetadata' in self.request.json
        if self.skill_has_settings:
            skill_metadata = self.request.json['skillMetadata']
            self.default_settings = {}
            normalized_sections = []
            for section in skill_metadata['sections']:
                for field in section['fields']:
                    if field['type'] != 'label':
                        field['value'] = _normalize_field_value(field)
                        self.default_settings[field['name']] = field['value']
                normalized_sections.append(section)
            self.request.json['skillMetadata'].update(
                sections=normalized_sections
            )

    def _update_skill_settings_definition(self):
        settings_def_repo = SettingsDisplayRepository(self.db)
        self.settings_definition_id = settings_def_repo.upsert(
            self.skill.id,
            self.request.json
        )

    def _update_device_skill(self, device_id):
        device_skill_repo = DeviceSkillRepository(self.db)
        device_skill = device_skill_repo.get_skill_settings_for_device(
            device_id,
            self.skill_id
        )
        if device_skill is None:
            error_msg = 'Received skill setting definition before manifest'
            _log.error(error_msg)
            raise DataError
        else:
            device_skill.settings_display_id = self.settings_definition_id
            if self.skill_has_settings:
                device_skill.settings_values = self._reconcile_skill_settings(
                    device_skill.settings_values
                )
            device_skill_repo.update_device_skill_settings(
                device_id,
                device_skill
            )

    def _reconcile_skill_settings(self, settings_values):
        new_settings_values = {}
        if settings_values is None:
            new_settings_values = self.default_settings
        else:
            for name, value in self.default_settings.items():
                if name in settings_values:
                    new_settings_values[name] = settings_values[name]
                else:
                    new_settings_values[name] = self.default_settings[name]
            for name, value in settings_values.items():
                if name in self.default_settings:
                    new_settings_values[name] = settings_values[name]

        return new_settings_values
