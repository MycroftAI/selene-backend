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

"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict
from http import HTTPStatus
from typing import List

from selene.api import SeleneEndpoint
from selene.data.skill import SkillDisplay, SkillDisplayRepository
from selene.util.log import get_selene_logger

_log = get_selene_logger(__name__)


class AvailableSkillsEndpoint(SeleneEndpoint):
    """Marketplace endpoint to get all the skills available in the market."""

    authentication_required = False

    def __init__(self):
        super().__init__()
        self.available_skills: List[SkillDisplay] = []
        self.response_skills: List[dict] = []
        self.skills_in_manifests = defaultdict(list)

    def get(self):
        """Handles a HTTP GET request."""
        self._get_available_skills()
        self._build_response_data()
        self.response = (dict(skills=self.response_skills), HTTPStatus.OK)

        return self.response

    def _get_available_skills(self):
        """Retrieve all skills in the skill repository.

        The data is retrieved from a database table that is populated with
        the contents of a JSON object in the mycroft-skills-data Github
        repository.  The JSON object contains metadata about each skill.
        """
        display_repo = SkillDisplayRepository(self.db)
        self.available_skills = display_repo.get_display_data_for_skills()

    def _build_response_data(self):
        """Build the data to include in the response."""
        if self.request.query_string:
            skills_to_include = self._filter_skills()
        else:
            skills_to_include = self.available_skills
        self._reformat_skills(skills_to_include)
        self._sort_skills()

    def _filter_skills(self) -> list:
        """If search criteria exist, only return those skills that match."""
        skills_to_include = []

        query_string = self.request.query_string.decode()
        search_term = query_string.lower().split("=")[1]
        for skill in self.available_skills:
            display_data = skill.display_data
            search_term_match = (
                search_term is None
                or search_term in display_data["title"].lower()
                or search_term in display_data["description"].lower()
                or search_term in display_data["short_desc"].lower()
                or search_term in [c.lower() for c in display_data["categories"]]
                or search_term in [t.lower() for t in display_data["tags"]]
                or search_term in [t.lower() for t in display_data["examples"]]
            )
            if search_term_match:
                skills_to_include.append(skill)

        return skills_to_include

    def _reformat_skills(self, skills_to_include: List[SkillDisplay]):
        """Build the response data from the skill service response"""
        for skill in skills_to_include:
            skill_info = dict(
                displayName=skill.display_data.get("display_name"),
                icon=skill.display_data.get("icon"),
                iconImage=skill.display_data.get("icon_img"),
                isMycroftMade=False,
                isSystemSkill=False,
                marketCategory="Undefined",
                id=skill.id,
                summary=skill.display_data.get("short_desc"),
                trigger=None,
            )
            examples = skill.display_data.get("examples")
            if examples is not None and examples:
                skill_info.update(trigger=skill.display_data["examples"][0])
            tags = skill.display_data.get("tags")
            if tags is not None and "system" in tags:
                skill_info.update(isSystemSkill=True)
            categories = skill.display_data.get("categories")
            if categories is not None and categories:
                skill_info.update(marketCategory=categories[0])
            skill_credits = skill.display_data.get("credits")
            if skill_credits is not None:
                credits_names = [credit.get("name") for credit in skill_credits]
                if "Mycroft AI" in credits_names:
                    skill_info.update(isMycroftMade=True)
            self.response_skills.append(skill_info)

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        sorted_skills = sorted(
            self.response_skills, key=lambda skill: skill["displayName"]
        )
        self.response_skills = sorted_skills
