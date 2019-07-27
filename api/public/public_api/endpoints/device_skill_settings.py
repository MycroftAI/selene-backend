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

import json
from http import HTTPStatus

from flask import Response
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import StringType, BooleanType, ListType, ModelType

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository
from selene.data.device import DeviceSkillRepository
from selene.data.skill import (
    SettingsDisplay,
    SettingsDisplayRepository,
    Skill,
    SkillRepository,
    SkillSettingRepository
)
from selene.util.cache import DEVICE_SKILL_ETAG_KEY

# matches <submodule_name>|<branch>
GLOBAL_ID_PATTERN = '^([^\|@]+)\|([^\|]+$)'
# matches @<device_id>|<submodule_name>|<branch>
GLOBAL_ID_DIRTY_PATTERN = '^@(.*)\|(.*)\|(.*)$'
# matches @<device_id>|<folder_name>
GLOBAL_ID_NON_MSM_PATTERN = '^@([^\|]+)\|([^\|]+$)'
GLOBAL_ID_ANY_PATTERN = '(?:{})|(?:{})|(?:{})'.format(
    GLOBAL_ID_PATTERN,
    GLOBAL_ID_DIRTY_PATTERN,
    GLOBAL_ID_NON_MSM_PATTERN
)


class SkillSettingUpdater(object):
    """Update the settings data for all devices with a skill

    Skills and their settings are global across devices.  While the PUT
    request specifies a single device to update, all devices with
    the same skill must be updated as well.
    """
    _device_skill_repo = None
    _settings_display_repo = None

    def __init__(self, db, device_id, display_data: dict):
        self.db = db
        self.device_id = device_id
        self.display_data = display_data
        self.settings_values = None
        self.skill = None

    @property
    def device_skill_repo(self):
        if self._device_skill_repo is None:
            self._device_skill_repo = DeviceSkillRepository(self.db)

        return self._device_skill_repo

    @property
    def settings_display_repo(self):
        if self._settings_display_repo is None:
            self._settings_display_repo = SettingsDisplayRepository(self.db)

        return self._settings_display_repo

    def update(self):
        self._extract_settings_values()
        self._get_skill_id()
        self._ensure_settings_display_exists()
        self._upsert_device_skill()

    def _extract_settings_values(self):
        """Extract the settings values from the skillMetadata

        The device applies the settings values in settings.json to the
        settings_meta.json file before sending the result to this API.  The
        settings values are stored separately from the metadata in the database.
        """
        settings_definition = self.display_data.get('skillMetadata')
        if settings_definition is not None:
            self.settings_values = dict()
            sections_without_values = []
            for section in settings_definition['sections']:
                section_without_values = dict(**section)
                for field in section_without_values['fields']:
                    field_name = field.get('name')
                    field_value = field.get('value')
                    if field_value is not None:
                        if field_name is not None:
                            self.settings_values[field_name] = field_value
                        del(field['value'])
                sections_without_values.append(section_without_values)
            settings_definition['sections'] = sections_without_values

    def _get_skill_id(self):
        """Get the id of the skill in the request"""
        skill_global_id = (
                self.display_data.get('skill_gid') or
                self.display_data.get('identifier')
        )
        skill_repo = SkillRepository(self.db)
        skill_id = skill_repo.ensure_skill_exists(skill_global_id)
        self.skill = Skill(skill_global_id, skill_id)

    def _ensure_settings_display_exists(self) -> bool:
        """If the settings display changed, a new row needs to be added."""
        new_settings_display = False
        self.settings_display = SettingsDisplay(
            self.skill.id,
            self.display_data
        )
        self.settings_display.id = (
            self.settings_display_repo.get_settings_display_id(
                self.settings_display
            )
        )
        if self.settings_display.id is None:
            self.settings_display.id = self.settings_display_repo.add(
                self.settings_display
            )
            new_settings_display = True

        return new_settings_display

    def _upsert_device_skill(self):
        """Update the account's devices with the skill to have new settings"""
        skill_settings = self._get_account_skill_settings()
        device_skill_found = self._update_skill_settings(skill_settings)
        if not device_skill_found:
            self._add_skill_to_device()

    def _get_account_skill_settings(self):
        """Get all the permutations of settings for a skill"""
        account_repo = AccountRepository(self.db)
        account = account_repo.get_account_by_device_id(self.device_id)
        skill_settings = (
            self.device_skill_repo.get_device_skill_settings_for_account(
                account.id,
                self.skill.id
            )
        )

        return skill_settings

    def _update_skill_settings(self, skill_settings):
        device_skill_found = False
        for skill_setting in skill_settings:
            if self.device_id in skill_setting.device_ids:
                device_skill_found = True
                if skill_setting.install_method in ('voice', 'cli'):
                    devices_to_update = [self.device_id]
                else:
                    devices_to_update = skill_setting.device_ids
                self.device_skill_repo.upsert_device_skill_settings(
                    devices_to_update,
                    self.settings_display,
                    self.settings_values if self.settings_values else None
                )
                break

        return device_skill_found

    def _add_skill_to_device(self):
        """Add a device_skill row for this skill.

        In theory, the skill manifest endpoint handles adding skills to a
        device but testing shows that this endpoint gets called before the
        manifest endpoint in some cases.
        """
        self.device_skill_repo.upsert_device_skill_settings(
            [self.device_id],
            self.settings_display,
            self.settings_values if self.settings_values else None
        )


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


class RequestSkill(Model):
    name = StringType()
    skill_gid = StringType(regex=GLOBAL_ID_ANY_PATTERN)
    skillMetadata = ModelType(RequestSkillMetadata)
    icon_img = StringType()
    icon = ModelType(RequestSkillIcon)
    display_name = StringType()
    color = StringType()
    identifier = StringType()

    def validate_skill_gid(self, data, value):
        if data['skill_gid'] is None and data['identifier'] is None:
            raise ValidationError(
                'skill should have either skill_gid or identifier defined'
            )
        return value


class DeviceSkillSettingsEndpoint(PublicEndpoint):
    """Fetch all skills associated with a device using the API v1 format"""
    _device_skill_repo = None
    _skill_repo = None
    _skill_setting_repo = None
    _settings_display_repo = None

    @property
    def device_skill_repo(self):
        if self._device_skill_repo is None:
            self._device_skill_repo = DeviceSkillRepository(self.db)

        return self._device_skill_repo

    @property
    def settings_display_repo(self):
        if self._settings_display_repo is None:
            self._settings_display_repo = SettingsDisplayRepository(self.db)

        return self._settings_display_repo

    @property
    def skill_repo(self):
        if self._skill_repo is None:
            self._skill_repo = SkillRepository(self.db)

        return self._skill_repo

    @property
    def skill_setting_repo(self):
        if self._skill_setting_repo is None:
            self._skill_setting_repo = SkillSettingRepository(self.db)

        return self._skill_setting_repo

    def get(self, device_id):
        """
        Retrieve skills installed on device from the database.

        :raises NotModifiedException: when etag in request matches cache
        """
        self._authenticate(device_id)
        self._validate_etag(DEVICE_SKILL_ETAG_KEY.format(device_id=device_id))
        device_skills = self.skill_setting_repo.get_skill_settings_for_device(
            device_id
        )

        if device_skills:
            response_data = self._build_response_data(device_skills)
            response = Response(
                json.dumps(response_data),
                status=HTTPStatus.OK,
                content_type='application/json'
            )
            self._add_etag(DEVICE_SKILL_ETAG_KEY.format(device_id=device_id))
        else:
            response = Response(
                '',
                status=HTTPStatus.NO_CONTENT,
                content_type='application/json'
            )
        return response

    def _build_response_data(self, device_skills):
        response_data = []
        for skill in device_skills:
            response_skill = dict(uuid=skill.skill_id)
            settings_definition = skill.settings_display.get('skillMetadata')
            if settings_definition:
                settings_sections = self._apply_settings_values(
                    settings_definition, skill.settings_values
                )
                if settings_sections:
                    response_skill.update(
                        skillMetadata=dict(sections=settings_sections)
                    )
            skill_gid = skill.settings_display.get('skill_gid')
            if skill_gid is not None:
                response_skill.update(skill_gid=skill_gid)
            identifier = skill.settings_display.get('identifier')
            if identifier is not None:
                response_skill.update(identifier=identifier)
            response_data.append(response_skill)

        return response_data

    @staticmethod
    def _apply_settings_values(settings_definition, settings_values):
        """Build a copy of the settings sections populated with values."""
        sections_with_values = []
        for section in settings_definition['sections']:
            section_with_values = dict(**section)
            for field in section_with_values['fields']:
                field_name = field.get('name')
                if field_name is not None and field_name in settings_values:
                    field.update(value=settings_values[field_name])
            sections_with_values.append(section_with_values)

        return sections_with_values

    def put(self, device_id):
        self._authenticate(device_id)
        self._validate_put_request()
        skill_id = self._update_skill_settings(device_id)
        self.etag_manager.expire(
            DEVICE_SKILL_ETAG_KEY.format(device_id=device_id)
        )

        return dict(uuid=skill_id), HTTPStatus.OK

    def _validate_put_request(self):
        skill = RequestSkill(self.request.json)
        skill.validate()

    def _update_skill_settings(self, device_id):
        skill_setting_updater = SkillSettingUpdater(
            self.db,
            device_id,
            self.request.json
        )
        skill_setting_updater.update()
        self._delete_orphaned_settings_display(
            skill_setting_updater.settings_display.id
        )

        return skill_setting_updater.skill.id

    def delete(self, device_id, skill_gid):
        self._authenticate(device_id)
        skill = self.skill_repo.get_skill_by_global_id(skill_gid)
        settings_display_id = self._delete_skill_from_device(device_id, skill)
        self._delete_orphaned_settings_display(settings_display_id)
        return '', HTTPStatus.OK

    def _delete_skill_from_device(self, device_id, skill):
        settings_display_id = None
        device_skills = (
            self.device_skill_repo.get_device_skill_settings_for_device(
                device_id
            )
        )
        for device_skill in device_skills:
            if device_skill.skill_id == skill.id:
                self.device_skill_repo.remove(device_id, skill.id)
                settings_display_id = device_skill.settings_display_id

        return settings_display_id

    def _delete_orphaned_settings_display(self, settings_display_id):
        skill_count = self.device_skill_repo.get_settings_display_usage(
            settings_display_id
        )
        if not skill_count:
            self.settings_display_repo.remove(settings_display_id)
