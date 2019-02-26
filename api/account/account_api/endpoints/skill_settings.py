from http import HTTPStatus

from selene.api.base_endpoint import SeleneEndpoint
from selene.data.account import AccountSkill, AccountSkillRepository
from selene.util.db import get_db_connection


class SkillSettingsEndpoint(SeleneEndpoint):
    def __init__(self):
        super(SkillSettingsEndpoint, self).__init__()
        self.account_skills = None

    def get(self):
        self._authenticate()
        self._get_skill_settings()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _get_skill_settings(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skill_repository = AccountSkillRepository(db, self.account.id)
            self.account_skills = skill_repository.get_skills_for_account()

    def _build_response_data(self):
        response_data = []
        for skill in self.account_skills:
            response_skill = dict(name=skill.skill_name)
            if skill.settings_version is not None:
                duplicates = self._check_for_skill_duplicates()
                response_sections = self._build_sections(skill, duplicates)
                response_skill.update(sections=response_sections)
            response_data.append(response_skill)

        return response_data

    def _check_for_skill_duplicates(self):
        distinct_skills = set()
        duplicate_skills = set()
        for skill in self.account_skills:
            if skill.skill_name in distinct_skills:
                duplicate_skills.add(skill.skill_name)
            distinct_skills.add(skill.skill_name)

        return duplicate_skills

    def _build_sections(self, skill: AccountSkill, duplicates: set):
        response_sections = []
        if skill.skill_name in duplicates:
            label_setting = dict(type='label', label=', '.join(skill.devices))
            response_sections.append(
                dict(name='Devices', settings=[label_setting])
            )
        for section in skill.settings_meta['skillMetadata']['sections']:
            section_settings = self._build_section_settings(
                section,
                skill.settings
            )
            response_sections.append(
                dict(name=section['name'], settings=section_settings)
            )

        return response_sections

    @staticmethod
    def _build_section_settings(section, skill_settings):
        section_settings = []
        for field in section['fields']:
            response_field = {key: value for key, value in field.items()}
            field_name = response_field.get('name')
            if field_name is not None:
                response_field['value'] = skill_settings[field_name]
            if response_field['type'] == 'select':
                parsed_options = []
                for option in response_field['options'].split(';'):
                    display, value = option.split('|')
                    parsed_options.append(dict(display=display, value=value))
                response_field['options'] = parsed_options
            section_settings.append(response_field)

        return section_settings
