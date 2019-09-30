# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import List

from ..entity.skill import Skill, SkillFamily
from ...repository_base import RepositoryBase


def extract_family_from_global_id(skill_gid):
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

    def get_skills_for_account(self, account_id) -> List[SkillFamily]:
        skills = []
        db_request = self._build_db_request(
            'get_skills_for_account.sql',
            args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_all(db_request)
        if db_result is not None:
            for row in db_result:
                skills.append(SkillFamily(**row))

        return skills

    def get_skill_by_global_id(self, skill_global_id) -> Skill:
        return self._select_one_into_dataclass(
            dataclass=Skill,
            sql_file_name='get_skill_by_global_id.sql',
            args=dict(skill_global_id=skill_global_id)
        )

    @staticmethod
    def _extract_settings(skill):
        settings = {}
        skill_metadata = skill.get('skillMetadata')
        if skill_metadata:
            for section in skill_metadata['sections']:
                for field in section['fields']:
                    if 'name' in field and 'value' in field:
                        settings[field['name']] = field['value']
                    field.pop('value', None)
            result = settings, skill
        else:
            result = '', ''
        return result

    def ensure_skill_exists(self, skill_global_id: str) -> str:
        skill = self.get_skill_by_global_id(skill_global_id)
        if skill is None:
            family_name = extract_family_from_global_id(skill_global_id)
            skill_id = self._add_skill(skill_global_id, family_name)
        else:
            skill_id = skill.id

        return skill_id

    def _add_skill(self, skill_gid: str, name: str) -> str:
        db_request = self._build_db_request(
            sql_file_name='add_skill.sql',
            args=dict(skill_gid=skill_gid, family_name=name)
        )
        db_result = self.cursor.insert_returning(db_request)

        # handle both dictionary cursors and namedtuple cursors
        try:
            skill_id = db_result['id']
        except TypeError:
            skill_id = db_result.id

        return skill_id

    def remove_by_gid(self, skill_gid):
        db_request = self._build_db_request(
            sql_file_name='remove_skill_by_gid.sql',
            args=dict(skill_gid=skill_gid)
        )
        self.cursor.delete(db_request)
