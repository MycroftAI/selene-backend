"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict
from http import HTTPStatus
from logging import getLogger
from typing import List

import requests as service_request

from selene_util.api import APIError, SeleneEndpoint
from .common import RepositorySkill

_log = getLogger(__package__)


class AvailableSkillsEndpoint(SeleneEndpoint):
    authentication_required = False

    def __init__(self):
        super(AvailableSkillsEndpoint, self).__init__()
        self.available_skills: List[RepositorySkill] = []
        self.response_skills: List[dict] = []
        self.skills_in_manifests = defaultdict(list)

    def get(self):
        try:
            self._get_available_skills()
        except APIError:
            pass
        else:
            self._build_response_data()
            self.response = (self.response_skills, HTTPStatus.OK)

        return self.response

    def _get_available_skills(self):
        """Retrieve all skills in the skill repository.

        The data is retrieved from a database table that is populated with
        the contents of a JSON object in the mycroft-skills-data Github
        repository.  The JSON object contains metadata about each skill.
        """
        skill_service_response = service_request.get(
            self.config['SELENE_BASE_URL'] + '/skill/all'
        )
        if skill_service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(skill_service_response)
        self.available_skills = [
            RepositorySkill(**skill) for skill in skill_service_response.json()
        ]

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
        search_term = query_string.lower().split('=')[1]
        for skill in self.available_skills:
            search_term_match = (
                search_term is None or
                search_term in skill.title.lower() or
                search_term in skill.description.lower() or
                search_term in skill.summary.lower() or
                search_term in [c.lower() for c in skill.categories] or
                search_term in [t.lower() for t in skill.tags] or
                search_term in [t.lower() for t in skill.triggers]
            )
            if search_term_match:
                skills_to_include.append(skill)

        return skills_to_include

    def _reformat_skills(self, skills_to_include: List[RepositorySkill]):
        """Build the response data from the skill service response"""
        for skill in skills_to_include:
            skill_info = dict(
                icon=skill.icon,
                iconImage=skill.icon_image,
                isMycroftMade=skill.is_mycroft_made,
                isSystemSkill=skill.is_system_skill,
                marketCategory=skill.market_category,
                name=skill.skill_name,
                summary=skill.summary,
                title=skill.title,
                trigger=skill.triggers[0]
            )
            self.response_skills.append(skill_info)

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        sorted_skills = sorted(
            self.response_skills,
            key=lambda skill:
            skill['title']
        )
        self.response_skills = sorted_skills
