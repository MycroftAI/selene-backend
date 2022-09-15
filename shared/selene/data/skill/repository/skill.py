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
"""Data access methods for the skill.skill table."""
from typing import List

from ..entity.skill import Skill, SkillFamily
from ...repository_base import RepositoryBase


def extract_family_from_global_id(skill_gid: str) -> str:
    """Extracts a common skill name for different GIDs of the same skill.

    :param skill_gid: The global identifier of the skill.
    :returns: Common name for skill for use in GUI
    """
    id_parts = skill_gid.split("|")
    if id_parts[0].startswith("@"):
        family_name = id_parts[1]
    else:
        family_name = id_parts[0]

    if skill_gid.endswith(".mark2"):
        family_name = skill_gid[: -len(".mark2")]

    return family_name


class SkillRepository(RepositoryBase):
    """Defines data access methods for the skill.skill table."""

    def __init__(self, db):
        self.db = db
        super().__init__(db, __file__)

    def get_skills_for_account(self, account_id: str) -> List[SkillFamily]:
        """Retrieves a list of distinct skills on all devices for an account.

        :param account_id: the internal identifier of the account
        :returns: a list of skills by skill family name
        """
        skills = []
        db_request = self._build_db_request(
            "get_skills_for_account.sql", args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_all(db_request)
        if db_result is not None:
            for row in db_result:
                skills.append(SkillFamily(**row))

        return skills

    def get_skill_by_global_id(self, skill_global_id: str) -> Skill:
        """Retrieves a skill from the database using its Global ID.

        :param skill_global_id: Identifier of a skill
        :returns the entry on the skill table for the provided global ID
        """
        return self._select_one_into_dataclass(
            dataclass=Skill,
            sql_file_name="get_skill_by_global_id.sql",
            args=dict(skill_global_id=skill_global_id),
        )

    def ensure_skill_exists(self, skill_global_id: str) -> str:
        """Adds skill to the database if its global id does not already exist.

        :param skill_global_id: identifier of a skill
        :return: the internal identifier for the skill
        """
        skill = self.get_skill_by_global_id(skill_global_id)
        if skill is None:
            family_name = extract_family_from_global_id(skill_global_id)
            skill_id = self._add_skill(skill_global_id, family_name)
        else:
            skill_id = skill.id

        return skill_id

    def _add_skill(self, skill_gid: str, name: str) -> str:
        """Adds a skill to the database.

        :param skill_gid: identifier of a skill
        :param name: human readable skill name
        :return: internal identifier of the new skill
        """
        db_request = self._build_db_request(
            sql_file_name="add_skill.sql",
            args=dict(skill_gid=skill_gid, family_name=name),
        )
        db_result = self.cursor.insert_returning(db_request)

        # handle both dictionary cursors and namedtuple cursors
        try:
            skill_id = db_result["id"]
        except TypeError:
            skill_id = db_result.id

        return skill_id

    def remove_by_gid(self, skill_gid):
        """Deletes a skill from the database.

        :param skill_gid: identifier of a skill
        """
        db_request = self._build_db_request(
            sql_file_name="remove_skill_by_gid.sql", args=dict(skill_gid=skill_gid)
        )
        self.cursor.delete(db_request)
