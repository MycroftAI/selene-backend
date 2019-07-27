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

"""Endpoint to return the skill settings for a given skill family."""
from http import HTTPStatus

from flask import json, Response

from selene.api import SeleneEndpoint
from selene.api.etag import ETagManager
from selene.data.skill import SkillSettingRepository, AccountSkillSetting


class SkillSettingsEndpoint(SeleneEndpoint):
    _setting_repository = None

    def __init__(self):
        super(SkillSettingsEndpoint, self).__init__()
        self.account_skills = None
        self.family_settings = None
        self.etag_manager: ETagManager = ETagManager(
            self.config['SELENE_CACHE'],
            self.config
        )

    @property
    def setting_repository(self):
        """Only instantiate the SkillSettingsRepository if needed."""
        if self._setting_repository is None:
            self._setting_repository = SkillSettingRepository(self.db)

        return self._setting_repository

    def get(self, skill_family_name):
        """Process an HTTP GET request"""
        self._authenticate()
        self.family_settings = self.setting_repository.get_family_settings(
            self.account.id,
            skill_family_name
        )
        self._parse_selection_options()
        response_data = self._build_response_data()

        # The response object is manually built here to bypass the
        # camel case conversion so settings are displayed correctly
        return Response(
            response=json.dumps(response_data),
            status=HTTPStatus.OK,
            content_type='application/json'
        )

    def _parse_selection_options(self):
        """Parse the dropdown options string into a list of options.

        Drop-down options are defined in a skill's settingsmeta.json as such:
            <label 1>|<value 1>;<label 2>|<value 2>;<label 3>|<value 3>...etc
        Convert this string into a dictionary where the key is the label and
        the value is the value.
        """
        for skill_settings in self.family_settings:
            if skill_settings.settings_display is not None:
                for section in skill_settings.settings_display['sections']:
                    for field in section['fields']:
                        if field['type'] == 'select':
                            parsed_options = []
                            for option in field['options'].split(';'):
                                option_display, option_value = option.split('|')
                                parsed_options.append(
                                    dict(
                                        display=option_display,
                                        value=option_value
                                    )
                                )
                            field['options'] = parsed_options

    def _build_response_data(self):
        """Build the object to return to the UI."""
        response_data = []
        for skill_settings in self.family_settings:
            # The UI will throw an error if settings display is null due to how
            # the skill settings data structures are defined.
            if skill_settings.settings_display is None:
                skill_settings.settings_display = dict(sections=[])
            response_skill = dict(
                settingsDisplay=skill_settings.settings_display,
                settingsValues=skill_settings.settings_values,
                deviceNames=skill_settings.device_names
            )
            response_data.append(response_skill)

        return response_data

    def put(self, skill_family_name):
        """Process a HTTP PUT request"""
        self._authenticate()
        self._update_settings_values()

        return '', HTTPStatus.OK

    def _update_settings_values(self):
        """Update the value of the settings column on the device_skill table,"""
        for new_skill_settings in self.request.json['skillSettings']:
            account_skill_settings = AccountSkillSetting(
                settings_display=new_skill_settings['settingsDisplay'],
                settings_values=new_skill_settings['settingsValues'],
                device_names=new_skill_settings['deviceNames']
            )
            self.setting_repository.update_skill_settings(
                self.account.id,
                account_skill_settings,
                self.request.json['skillIds']
            )
        self.etag_manager.expire_skill_etag_by_account_id(self.account.id)
