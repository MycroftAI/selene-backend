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

"""View to return detailed information about a skill"""
from http import HTTPStatus

from markdown import markdown

from selene.api import SeleneEndpoint
from selene.data.skill import SkillDisplay, SkillDisplayRepository


class SkillDetailEndpoint(SeleneEndpoint):
    """Supply the data that will populate the skill detail page."""

    authentication_required = False

    def __init__(self):
        super().__init__()
        self.skill_display_id = None
        self.response_skill = None
        self.manifest_skills = []

    def get(self, skill_display_id):
        """Process an HTTP GET request"""
        self.skill_display_id = skill_display_id
        skill_display = self._get_skill_details()
        self._build_response_data(skill_display)
        self.response = (self.response_skill, HTTPStatus.OK)

        return self.response

    def _get_skill_details(self) -> SkillDisplay:
        """Build the data to include in the response."""
        display_repository = SkillDisplayRepository(self.db)
        skill_display = display_repository.get_display_data_for_skill(
            self.skill_display_id
        )

        return skill_display

    def _build_response_data(self, skill_display: SkillDisplay):
        """Make some modifications to the response skill for the marketplace"""
        self.response_skill = dict(
            categories=skill_display.display_data.get("categories"),
            credits=skill_display.display_data.get("credits"),
            description=markdown(
                skill_display.display_data.get("description"), output_format="html5"
            ),
            displayName=skill_display.display_data["display_name"],
            icon=skill_display.display_data.get("icon"),
            iconImage=skill_display.display_data.get("icon_img"),
            isSystemSkill=False,
            worksOnMarkOne=(
                "all" in skill_display.display_data["platforms"]
                or "platform_mark1" in skill_display.display_data["platforms"]
            ),
            worksOnMarkTwo=(
                "all" in skill_display.display_data["platforms"]
                or "platform_mark2" in skill_display.display_data["platforms"]
            ),
            worksOnPicroft=(
                "all" in skill_display.display_data["platforms"]
                or "platform_picroft" in skill_display.display_data["platforms"]
            ),
            worksOnKDE=(
                "all" in skill_display.display_data["platforms"]
                or "platform_plasmoid" in skill_display.display_data["platforms"]
            ),
            repositoryUrl=skill_display.display_data.get("repo"),
            summary=markdown(
                skill_display.display_data["short_desc"], output_format="html5"
            ),
            triggers=skill_display.display_data["examples"],
        )
        if skill_display.display_data["tags"] is not None:
            if "system" in skill_display.display_data["tags"]:
                self.response_skill["isSystemSkill"] = True
