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
        if self._setting_repository is None:
            self._setting_repository = SkillSettingRepository(self.db)

        return self._setting_repository

    def get(self, skill_family_name):
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
        response_data = []
        for skill_settings in self.family_settings:
            response_skill = dict(
                settingsDisplay=skill_settings.settings_display,
                settingsValues=skill_settings.settings_values,
                deviceNames=skill_settings.device_names
            )
            response_data.append(response_skill)

        return response_data

    def put(self, skill_family_name):
        self._authenticate()
        self._update_settings_values()

        return '', HTTPStatus.OK

    def _update_settings_values(self):
        for new_skill_settings in self.request.json['skillSettings']:
            account_skill_settings = AccountSkillSetting(
                settings_display=new_skill_settings['settingsDisplay'],
                settings_values=new_skill_settings['settingsValues'],
                device_names=new_skill_settings['deviceNames']
            )
            self.setting_repository.update_skill_settings(
                account_skill_settings,
                self.request.json['skillIds']
            )
        self.etag_manager.expire_skill_etag_by_account_id(self.account.id)
