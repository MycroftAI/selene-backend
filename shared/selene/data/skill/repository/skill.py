import json
from datetime import datetime
from typing import List

from selene.util.db import use_transaction
from .device_skill import DeviceSkillRepository
from .settings_display import SettingsDisplayRepository
from ..entity.skill import Skill
from ...repository_base import RepositoryBase


def _parse_skill_gid(skill_gid):
    id_parts = skill_gid.split('|')
    if id_parts[0].startswith('@'):
        family_name = id_parts[1]
    else:
        family_name = id_parts[0]

    return family_name


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
                    'skill_gid': result['settings_display']['skill_gid'],
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
                'skill_gid': sql_results['settings_display']['skill_gid'],
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
        skill_id = self.ensure_skill_exists(skill['skill_gid'])
        settings_value, settings_display = self._extract_settings(skill)
        settings_display = json.dumps(skill)
        skill_settings_display_id = SettingsDisplayRepository(self.db).add(skill_id, settings_display)
        settings_value = json.dumps(settings_value)
        DeviceSkillRepository(self.db).add(device_id, skill_id, skill_settings_display_id, settings_value)
        return skill_id

    def _add_skill(self, skill_gid: str, name: str) -> str:
        db_request = self._build_db_request(
            sql_file_name='add_skill.sql',
            args=dict(skill_gid=skill_gid, family_name=name)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']

    @staticmethod
    def _extract_settings(skill):
        settings = {}
        for section in skill['skillMetadata']['sections']:
            for field in section['fields']:
                if 'name' in field and 'value' in field:
                    settings[field['name']] = field['value']
                field.pop('value', None)
        return settings, skill

    def update_skills_manifest(self, device_id: str, skill_manifest: List[dict]):
        for skill in skill_manifest:
            skill['device_id'] = device_id
            self._convert_to_datetime(skill)
        db_batch_request = self._build_db_batch_request(
            'update_skill_manifest.sql',
            args=skill_manifest
        )
        self.cursor.batch_update(db_batch_request)

    def _convert_to_datetime(self, skill):
        installed = skill.get('installed')
        if installed:
            installed = datetime.fromtimestamp(installed)
            skill['installed'] = installed
        updated = skill.get('updated')
        if updated:
            updated = datetime.fromtimestamp(updated)
            skill['updated'] = updated

    def get_skills_manifest(self, device_id: str):
        db_request = self._build_db_request(
            sql_file_name='get_skills_manifest_by_device_id.sql',
            args=dict(device_id=device_id)
        )
        return self.cursor.select_all(db_request)

    def get_installer_skill(self):
        return self._select_one_into_dataclass(
            dataclass=Skill,
            sql_file_name='get_installer_skill_settings.sql'
        )

    def ensure_skill_exists(self, skill_gid: str) -> str:
        skill = self._select_one_into_dataclass(
            dataclass=Skill,
            sql_file_name='get_skill_by_global_id.sql',
            args=dict(skill_gid=skill_gid)
        )
        if skill is None:
            family_name = _parse_skill_gid(skill_gid)
            skill_id = self._add_skill(skill_gid, family_name)
        else:
            skill_id = skill.id

        return skill_id
