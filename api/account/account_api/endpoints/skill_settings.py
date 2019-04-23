from http import HTTPStatus

from flask import json

from selene.api import SeleneEndpoint, snake_to_camel
from selene.api.etag import ETagManager
from selene.data.skill import SkillSettingRepository


def _parse_selection_options(skill_settings):
    for skill_setting in skill_settings:
        for section in skill_setting.settings_display['sections']:
            for field in section['fields']:
                field_name = field.get('name')
                if field_name is not None:
                    field['name'] = snake_to_camel(field_name)
                if field['type'] == 'select':
                    parsed_options = []
                    for option in field['options'].split(';'):
                        option_display, option_value = option.split('|')
                        parsed_options.append(
                            dict(display=option_display, value=option_value)
                        )
                    field['options'] = parsed_options


class SkillSettingsEndpoint(SeleneEndpoint):
    def __init__(self):
        super(SkillSettingsEndpoint, self).__init__()
        self.account_skills = None
        self.etag_manager: ETagManager = ETagManager(
            self.config['SELENE_CACHE'],
            self.config
        )

    def get(self, skill_id):
        self._authenticate()
        skill_settings = self._get_skill_settings(skill_id)

        return skill_settings, HTTPStatus.OK

    def _get_skill_settings(self, skill_id: str):
        setting_repository = SkillSettingRepository(self.db)
        skill_settings = setting_repository.get_account_skill_settings(
            skill_id, self.account.id
        )

        _parse_selection_options(skill_settings)

        return skill_settings

    def put(self, skill_id):
        self._authenticate()
        request_data = json.loads(self.request.data)
        self._update_settings_values(skill_id, request_data['skillSettings'])

        return '', HTTPStatus.OK

    def _update_settings_values(self, skill_id, new_skill_settings):
        skill_settings_repository = SkillSettingRepository(self.db)
        skill_settings_repository.update_device_skill_settings(
            skill_id,
            new_skill_settings
        )
        self.etag_manager.expire_skill_etag_by_account_id(self.account.id)
