"""Data repository code for the skills on a device"""
from ..entity.device_skill import DeviceSkill
from ...repository_base import RepositoryBase


class DeviceSkillRepository(RepositoryBase):
    def __init__(self, db):
        super(DeviceSkillRepository, self).__init__(db, __file__)

    def get_installed_skills_for_account(self, account_id: str):
        return self._select_all_into_dataclass(
            dataclass=DeviceSkill,
            sql_file_name='get_device_skills_for_account.sql',
            args=dict(account_id=account_id)
        )

    def get_skills_for_device(self, device_id: str):
        return self._select_all_into_dataclass(
            dataclass=DeviceSkill,
            sql_file_name='get_skills_for_device.sql',
            args=dict(device_id=device_id)
        )

    def update_skill_settings(
            self, account_id: str, device_names: tuple, skill_name: str
    ):
        db_request = self._build_db_request(
            sql_file_name='update_skill_settings.sql',
            args=dict(
                account_id=account_id,
                device_names=device_names,
                skill_name=skill_name
            )
        )
        self.cursor.update(db_request)
