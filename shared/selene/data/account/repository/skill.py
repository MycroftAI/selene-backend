from collections import defaultdict
from typing import List

from selene.data.account.entity.skill import AccountSkill
from selene.data.repository_base import RepositoryBase


class AccountSkillRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(AccountSkillRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_skills_for_account(self) -> List[AccountSkill]:
        account_skills = []
        device_skills = self._get_device_skills()
        skill_settings_meta, device_groupings = self._group_devices(
            device_skills
        )

        for key, devices in device_groupings.items():
            display_name, settings_meta, settings = skill_settings_meta[key]
            account_skills.append(AccountSkill(
                skill_name=key[0],
                devices=devices,
                display_name=display_name,
                settings_version=key[1],
                settings_meta=settings_meta,
                settings=settings
            ))

        return account_skills    

    def _get_device_skills(self) -> dict:
        db_request = self._build_db_request(
            sql_file_name='get_account_skills.sql',
            args=dict(account_id=self.account_id)
        )
        db_result = self.cursor.select_all(db_request)

        return db_result

    @staticmethod
    def _group_devices(device_skills):
        device_groupings = defaultdict(list)
        skill_settings = {}
        for device_skill in device_skills:
            key = (
                device_skill['skill_name'],
                device_skill['version'],
            )
            device_groupings[key].append(device_skill['device_name'])
            skill_settings[key] = [
                device_skill['display_name'],
                device_skill['settings_meta'],
                device_skill['settings']
            ]

        return skill_settings, device_groupings
