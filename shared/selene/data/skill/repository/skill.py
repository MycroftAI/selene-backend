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
            return [result['skill'] for result in sql_results]

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
        sql_results = self.cursor.select_all(query)
        if sql_results:
            return sql_results[0]['skill']

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
