from typing import List

from ..entity.skill import Skill, SkillVersion
from ...repository_base import RepositoryBase


class SkillRepository(RepositoryBase):
    def __init__(self, db):
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
                    'name': result['name'],
                    'identifier': result['name'],
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
            sections = self._fill_setting_with_values(sql_results['settings'], sql_results['settings_meta'])
            skill = {
                'uuid': sql_results['id'],
                'name': sql_results['name'],
                'identifier': sql_results['name'],
                'skillMetadata': {
                    'sections': sections
                }
            }
            return skill

    def _fill_setting_with_values(self, settings: dict, setting_meta: dict):
        sections = setting_meta['skillMetadata']['sections']
        for section in sections:
            section_fields = section['fields']
            for field in section_fields:
                field['value'] = settings[field['name']]
        return setting_meta

    def get_skills_for_account(self, account_id) -> List[Skill]:
        skills = []
        db_request = self._build_db_request(
            'get_skills_for_account.sql',
            args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_all(db_request)
        if db_result is not None:
            for row in db_result:
                skill_versions = []
                if row['skill']['versions'] is not None:
                    for version in row['skill']['versions']:
                        skill_versions.append(SkillVersion(**version))
                    row['skill']['versions'] = skill_versions
                skills.append(Skill(**row['skill']))

        return skills
