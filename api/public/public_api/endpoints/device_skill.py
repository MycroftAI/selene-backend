"""Applies a skill settings definition to the database.

Whenever a change is made to a skill's settings definition on a device, the
updated definition is sent to the backend.

This endpoint assumes that the skill manifest is sent when the a device is
paired or a skill is installed. A skill that is not installed on a device
cannot send it's settings... right?  The skill and its relationship to the
device should already be known when this endpoint is called.
"""
from http import HTTPStatus
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
    SettingsDisplay,
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
        if field['value']:
            normalized_value = float(field['value'])
            if not normalized_value % 1:
                normalized_value = int(field['value'])
            else:
                normalized_value = 0
    elif field['value'] == "[]":
        normalized_value = []

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
        settings_definition_id = self._ensure_settings_definition_exists()
        self._update_device_skill(device_id, settings_definition_id)

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """Ensure the request is well-formed."""
        request_model = RequestDeviceSkill(self.request.json)
        request_model.validate()

    def _get_skill(self):
        """Retrieve the skill associated with the request."""
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
            raise DataError(dict(skill_gid=[err_msg]))

    def _parse_skill_metadata(self):
        """Inspect the contents of the skill settings definition.

        Skill authors often write settings definition files with strings in
        fields that should be boolean or numeric.  Ensure all fields are cast
        to the correct type before interacting with the database.
        """
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

    def _ensure_settings_definition_exists(self):
        """Add a row to skill.settings_display if it doesn't already exist."""
        settings_definition_id = None
        settings_def_repo = SettingsDisplayRepository(self.db)
        settings_defs = settings_def_repo.get_settings_definitions_by_gid(
            self.skill.skill_gid
        )

        for settings_def in settings_defs:
            if settings_def.display_data == self.request.json:
                settings_definition_id = settings_def.id
                break

        if settings_definition_id is None:
            settings_def_repo = SettingsDisplayRepository(self.db)
            settings_definition = SettingsDisplay(
                skill_id=self.skill.id,
                display_data=self.request.json
            )
            settings_definition_id = settings_def_repo.add(
                settings_definition
            )

        return settings_definition_id

    def _update_device_skill(self, device_id, settings_definition_id):
        """Update device.device_skill to match the new settings definition."""
        device_skill_repo = DeviceSkillRepository(self.db)
        device_skill = device_skill_repo.get_skill_settings_for_device(
            device_id,
            self.skill.id
        )
        if device_skill is None:
            error_msg = 'Received skill setting definition before manifest'
            _log.error(error_msg)
            raise DataError(dict(skill_gid=[error_msg]))
        else:
            device_skill.settings_display_id = settings_definition_id
            if self.skill_has_settings:
                device_skill.settings_values = self._reconcile_skill_settings(
                    device_skill.settings_values
                )
            device_skill_repo.update_device_skill_settings(
                device_id,
                device_skill
            )

    def _reconcile_skill_settings(self, settings_values):
        """Fix any new or removed settings."""
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
