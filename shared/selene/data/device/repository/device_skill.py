"""Data repository code for the skills on a device"""
from dataclasses import asdict
from typing import List

from ..entity.device_skill import DeviceSkill, ManifestSkill
from ...repository_base import RepositoryBase


class DeviceSkillRepository(RepositoryBase):
    def __init__(self, db):
        super(DeviceSkillRepository, self).__init__(db, __file__)

    def get_installed_skills_for_account(
            self, account_id: str
    ) -> List[DeviceSkill]:
        return self._select_all_into_dataclass(
            dataclass=DeviceSkill,
            sql_file_name='get_device_skills_for_account.sql',
            args=dict(account_id=account_id)
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

    def get_skill_manifest_for_device(self, device_id: str):
        return self._select_all_into_dataclass(
            dataclass=ManifestSkill,
            sql_file_name='get_device_skill_manifest.sql',
            args=dict(device_id=device_id)
        )

    def update_manifest_skill(self, manifest_skill: ManifestSkill):
        db_request = self._build_db_request(
            sql_file_name='update_skill_manifest.sql',
            args=asdict(manifest_skill)
        )

        self.cursor.update(db_request)

    def add_manifest_skill(self, skill_id: str, manifest_skill: ManifestSkill):
        db_request_args = dict(skill_id=skill_id)
        db_request_args.update(asdict(manifest_skill))
        db_request = self._build_db_request(
            sql_file_name='add_manifest_skill.sql',
            args=db_request_args
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']

    def remove_manifest_skill(self, manifest_skill: ManifestSkill):
        db_request = self._build_db_request(
            sql_file_name='remove_manifest_skill.sql',
            args=dict(
                device_id=manifest_skill.device_id,
                skill_gid=manifest_skill.skill_gid
            )
        )
        self.cursor.delete(db_request)
