import json
from typing import List

from selene.util.db import use_transaction
from .skill import SkillRepository
from ..entity.skill_setting import AccountSkillSetting, DeviceSkillSetting
from ...repository_base import RepositoryBase


class SkillSettingRepository(RepositoryBase):
    def __init__(self, db):
        super(SkillSettingRepository, self).__init__(db, __file__)
        self.db = db

    def get_family_settings(
            self,
            account_id: str,
            family_name: str
    ) -> List[AccountSkillSetting]:
        return self._select_all_into_dataclass(
            AccountSkillSetting,
            sql_file_name='get_settings_for_skill_family.sql',
            args=dict(family_name=family_name, account_id=account_id)
        )

    def get_installer_settings(self, account_id) -> List[AccountSkillSetting]:
        skill_repo = SkillRepository(self.db)
        skills = skill_repo.get_skills_for_account(account_id)
        installer_skill_id = None
        for skill in skills:
            if skill.display_name == 'Installer':
                installer_skill_id = skill.id

        skill_settings = None
        if installer_skill_id is not None:
            skill_settings = self.get_family_settings(
                account_id,
                installer_skill_id
            )

        return skill_settings

    @use_transaction
    def update_skill_settings(
            self,
            account_id,
            new_skill_settings: AccountSkillSetting,
            skill_ids: List[str]
    ):
        db_request = self._build_db_request(
            'update_device_skill_settings.sql',
            args=dict(
                account_id=account_id,
                settings_values=json.dumps(new_skill_settings.settings_values),
                skill_id=tuple(skill_ids),
                device_names=tuple(new_skill_settings.device_names)
            )
        )
        self.cursor.update(db_request)

    def get_skill_settings_for_device(self, device_id: str):
        """Return all skills and their settings for a given device id"""
        return self._select_all_into_dataclass(
            DeviceSkillSetting,
            sql_file_name='get_skill_setting_by_device.sql',
            args=dict(device_id=device_id)
        )
