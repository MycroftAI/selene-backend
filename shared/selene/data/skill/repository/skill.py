import json
from typing import List

from selene.util.db import use_transaction
from .device_skill import DeviceSkillRepository
from .settings_display import SettingsDisplayRepository
from ..entity.skill import Skill
from ...repository_base import RepositoryBase


class SkillRepository(RepositoryBase):
    def __init__(self, db):
        self.db = db
        super(SkillRepository, self).__init__(db, __file__)

    def get_skill_settings_by_device_id(self, device_id):
        """Return all skill settings from a given device id

        :param device_id: device uuid
        :return list of skills using the format from the API v1"""
        query = self._build_db_request(
            'get_skill_setting_by_device_id.sql',
            args=dict(device_id=device_id)
        )
        sql_results = self.cursor.select_all(query)
        if sql_results:
            skills = []
            for result in sql_results:
                sections = self._fill_setting_with_values(result['settings'], result['settings_display'])
                skill = {
                    'uuid': result['id'],
                    'name': result['settings_display']['name'],
                    'identifier': result['settings_display']['identifier'],
                    'skillMetadata': {
                        'sections': sections
                    }
                }
                skills.append(skill)
            return skills

    def get_skill_settings_by_device_id_and_version_hash(self, device_id, version_hash):
        """Return a skill setting for a given device id and skill version hash

        :param device_id: device uuid
        :param version_hash: skill setting version hash
        :return skill setting using the format from the API v1
        """
        query = self._build_db_request(
            'get_skill_setting_by_device_id_and_version_hash.sql',
            args=dict(device_id=device_id, version_hash=version_hash)
        )
        sql_results = self.cursor.select_one(query)
        if sql_results:
            sections = self._fill_setting_with_values(sql_results['settings'], sql_results['settings_display'])
            skill = {
                'uuid': sql_results['id'],
                'name': sql_results['settings_display']['name'],
                'identifier': sql_results['settings_display']['identifier'],
                'skillMetadata': {
                    'sections': sections
                }
            }
            return skill

    def _fill_setting_with_values(self, settings: dict, setting_meta: dict):
        sections = setting_meta['skillMetadata']['sections']
        if settings:
            for section in sections:
                section_fields = section['fields']
                for field in section_fields:
                    if 'name' in field:
                        name = field['name']
                        if name in settings:
                            field['value'] = settings[field['name']]
        return sections

    def get_skills_for_account(self, account_id) -> List[Skill]:
        skills = []
        db_request = self._build_db_request(
            'get_skills_for_account.sql',
            args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_all(db_request)
        if db_result is not None:
            for row in db_result:
                skills.append(Skill(**row['skill']))

        return skills

    @use_transaction
    def add(self, device_id: str, skill: dict) -> str:
        skill_id = self._add_skill(skill['name'])
        settings_value, settings_display = self._extract_settings(skill)
        settings_display = json.dumps(skill)
        skill_settings_display_id = SettingsDisplayRepository(self.db).add(skill_id, settings_display)
        settings_value = json.dumps(settings_value)
        DeviceSkillRepository(self.db).add(device_id, skill_id, skill_settings_display_id, settings_value)
        return skill_id

    def _add_skill(self, skill_name) -> str:
        db_request = self._build_db_request(
            'add_skill.sql',
            args=dict(skill_name=skill_name)
        )
        result = self.cursor.insert_returning(db_request)
        return result['id']

    @staticmethod
    def _extract_settings(skill):
        settings = {}
        for section in skill['skillMetadata']['sections']:
            for field in section['fields']:
                if 'name' in field and 'value' in field:
                    settings[field['name']] = field['value']
                field.pop('value', None)
        return settings, skill
