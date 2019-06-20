import json
from typing import List

from selene.util.db import use_transaction
from .skill import SkillRepository
from ..entity.skill_setting import AccountSkillSetting
from ...repository_base import RepositoryBase


class SkillSettingRepository(RepositoryBase):
    def __init__(self, db, account_id: str):
        super(SkillSettingRepository, self).__init__(db, __file__)
        self.db = db
        self.account_id = account_id

    def get_family_settings(self, family_name: str) -> List[AccountSkillSetting]:
        db_request = self._build_db_request(
            'get_settings_for_skill_family.sql',
            args=dict(family_name=family_name, account_id=self.account_id)
        )
        db_result = self.cursor.select_all(db_request)

        skill_settings = []
        for row in db_result:
            settings_display = row['settings_display']
            if settings_display is not None:
                settings_display = settings_display.get('skillMetadata')
            skill_settings.append(
                AccountSkillSetting(
                    settings_display=settings_display,
                    settings_values=row['settings_values'],
                    device_names=row['device_names'],
                )
            )

        return skill_settings

    def get_installer_settings(self) -> List[AccountSkillSetting]:
        skill_repo = SkillRepository(self.db)
        skills = skill_repo.get_skills_for_account(self.account_id)
        installer_skill_id = None
        for skill in skills:
            if skill.display_name == 'Installer':
                installer_skill_id = skill.id

        skill_settings = None
        if installer_skill_id is not None:
            skill_settings = self.get_family_settings(installer_skill_id)

        return skill_settings

    @use_transaction
    def update_skill_settings(
            self,
            new_skill_settings: AccountSkillSetting,
            skill_ids: List[str]
    ):
        db_request = self._build_db_request(
            'update_device_skill_settings.sql',
            args=dict(
                account_id=self.account_id,
                settings_values=json.dumps(new_skill_settings.settings_values),
                skill_id=tuple(skill_ids),
                device_names=tuple(new_skill_settings.device_names)
            )
        )
        self.cursor.update(db_request)
