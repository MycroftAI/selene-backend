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
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        skill_repository = SkillRepository(self.db)
        skills = skill_repository.get_skills_for_account(self.account.id)

        response_data = []
        for skill in skills:
            response_data.append(dict(
                family_name=skill.family_name,
                market_id=skill.market_id,
                name=skill.display_name or skill.family_name,
                has_settings=skill.has_settings,
                skill_ids=skill.skill_ids
            ))

        return sorted(response_data, key=lambda x: x['name'])
