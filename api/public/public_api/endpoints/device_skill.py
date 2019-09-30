# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Applies a skill settings definition to the database.

Whenever a change is made to a skill's settings definition on a device, this
endpoint is called to update the same on the database.  If a skill has
settings, the device's settings are also updated.

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
from selene.data.account import AccountRepository
from selene.data.device import DeviceSkillRepository
from selene.data.skill import (
    extract_family_from_global_id,
    SettingsDisplay,
    SettingsDisplayRepository,
    SkillRepository
)
from selene.data.skill import SkillSettingRepository

_log = getLogger(__package__)


def _normalize_field_value(field):
    """The field values in skillMetadata are all strings, convert to native."""
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
        self._device_skill_repo = None

    @property
    def device_skill_repo(self):
        if self._device_skill_repo is None:
            self._device_skill_repo = DeviceSkillRepository(self.db)

        return self._device_skill_repo

    def put(self, device_id):
        self._authenticate(device_id)
        self._validate_request()
        self._get_skill()
        self._parse_skill_metadata()
        self._ensure_settings_definition_exists()
        self._update_device_skill(device_id)

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
        self.settings_definition_id = None
        self._check_for_existing_settings_definition()
        if self.settings_definition_id is None:
            self._add_settings_definition()

    def _check_for_existing_settings_definition(self):
        """Look for an existing database row matching the request."""
        settings_def_repo = SettingsDisplayRepository(self.db)
        settings_defs = settings_def_repo.get_settings_definitions_by_gid(
            self.skill.skill_gid
        )
        for settings_def in settings_defs:
            if settings_def.display_data == self.request.json:
                self.settings_definition_id = settings_def.id
                break

    def _add_settings_definition(self):
        """The settings definition does not exist on database so add it."""
        settings_def_repo = SettingsDisplayRepository(self.db)
        settings_definition = SettingsDisplay(
            skill_id=self.skill.id,
            display_data=self.request.json
        )
        self.settings_definition_id = settings_def_repo.add(
            settings_definition
        )

    def _update_device_skill(self, device_id):
        """Update device.device_skill to match the new settings definition.

        If the skill has settings and the device_skill table does not, either
        use the default values in the settings definition or copy the settings
        from another device under the same account.
        """
        device_skill = self._get_device_skill(device_id)
        device_skill.settings_display_id = self.settings_definition_id
        if self.skill_has_settings:
            if device_skill.settings_values is None:
                new_settings_values = self._initialize_skill_settings(
                    device_id
                )
            else:
                new_settings_values = self._reconcile_skill_settings(
                    device_skill.settings_values
                )
            device_skill.settings_values = new_settings_values
        self.device_skill_repo.update_device_skill_settings(
            device_id,
            device_skill
        )

    def _get_device_skill(self, device_id):
        """Retrieve the device's skill entry from the database."""
        device_skill = self.device_skill_repo.get_skill_settings_for_device(
            device_id,
            self.skill.id
        )
        if device_skill is None:
            error_msg = (
                'Received skill setting definition before manifest for '
                'skill ' + self.skill.skill_gid
            )
            _log.error(error_msg)
            raise DataError(dict(skill_gid=[error_msg]))

        return device_skill

    def _reconcile_skill_settings(self, settings_values):
        """Fix any new or removed settings."""
        new_settings_values = {}
        for name, value in self.default_settings.items():
            if name in settings_values:
                new_settings_values[name] = settings_values[name]
            else:
                new_settings_values[name] = self.default_settings[name]
        for name, value in settings_values.items():
            if name in self.default_settings:
                new_settings_values[name] = settings_values[name]

        return new_settings_values

    def _initialize_skill_settings(self, device_id):
        """Use default settings or copy from another device in same account."""
        _log.info('Initializing settings for skill ' + self.skill.skill_gid)
        account_repo = AccountRepository(self.db)
        account = account_repo.get_account_by_device_id(device_id)
        skill_settings_repo = SkillSettingRepository(self.db)
        skill_family = extract_family_from_global_id(self.skill.skill_gid)
        family_settings = skill_settings_repo.get_family_settings(
            account.id,
            skill_family
        )
        new_settings_values = self.default_settings
        if family_settings is not None:
            for settings in family_settings:
                if settings.settings_values is None:
                    continue
                if settings.settings_values != self.default_settings:
                    field_names = settings.settings_values.keys()
                    if field_names == self.default_settings.keys():
                        _log.info(
                            'Copying settings from another device for skill' +
                            self.skill.skill_gid
                        )
                        new_settings_values = settings.settings_values
                        break
        else:
            _log.info(
                'Using default skill settings for skill ' +
                self.skill.skill_gid
            )

        return new_settings_values
