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

from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.skill import SkillRepository


class SkillsEndpoint(SeleneEndpoint):
    def get(self):
        """
        Returns the authentication data.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        """
        Builds a skill data

        Args:
            self: (todo): write your description
        """
        skill_repository = SkillRepository(self.db)
        skills = skill_repository.get_skills_for_account(self.account.id)

        response_data = {}
        for skill in skills:
            try:
                response_skill = response_data[skill.family_name]
            except KeyError:
                response_data[skill.family_name] = dict(
                    family_name=skill.family_name,
                    market_id=skill.market_id,
                    name=skill.display_name or skill.family_name,
                    has_settings=skill.has_settings,
                    skill_ids=skill.skill_ids
                )
            else:
                response_skill['skill_ids'].extend(skill.skill_ids)
                if response_skill['market_id'] is None:
                    response_skill['market_id'] = skill.market_id

        return sorted(response_data.values(), key=lambda x: x['name'])
