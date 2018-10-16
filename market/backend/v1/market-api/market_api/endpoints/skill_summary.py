"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict
from dataclasses import dataclass, field
from http import HTTPStatus
from logging import getLogger
from typing import List

from markdown import markdown
import requests as service_request

from .common import (
    aggregate_manifest_skills,
    call_skill_manifest_endpoint,
    parse_skill_manifest_response
)
from selene_util.api import APIError, SeleneEndpoint

DEFAULT_ICON_COLOR = '#6C7A89'
DEFAULT_ICON_NAME = 'comment-alt'
SYSTEM_CATEGORY = 'System'
UNDEFINED_CATEGORY = 'Not Categorized'

_log = getLogger(__package__)


@dataclass
class RepositorySkill(object):
    """Represents a single skill defined in the Mycroft Skills repository."""
    branch: str
    categories: List[str]
    created: str
    credits: List[str]
    description: str
    id: str
    last_update: str
    platforms: List[str]
    repository_owner: str
    repository_url: str
    skill_name: str
    summary: str
    tags: List[str]
    title: str
    triggers: List[str]
    icon: dict
    icon_image: str = field(default=None)
    marketplace_category: str = field(init=False, default=UNDEFINED_CATEGORY)

    def __post_init__(self):
        if 'system' in self.tags:
            self.marketplace_category = SYSTEM_CATEGORY
        elif self.categories:
            # a skill may have many categories.  the first one in the
            # list is considered the "primary" category.  This is the
            # category the marketplace will use to group the skill.
            self.marketplace_category = self.categories[0]
        if not self.icon:
            self.icon = dict(icon=DEFAULT_ICON_NAME, color=DEFAULT_ICON_COLOR)


class SkillSummaryEndpoint(SeleneEndpoint):
    authentication_required = False

    def __init__(self):
        super(SkillSummaryEndpoint, self).__init__()
        self.available_skills: List[RepositorySkill] = []
        self.response_skills = defaultdict(list)
        self.skills_in_manifests = defaultdict(list)

    def get(self):
        try:
            self._authenticate()
            self._get_skills()
        except APIError:
            pass
        else:
            self._build_response_data()
            self.response = (self.response_skills, HTTPStatus.OK)

        return self.response

    def _get_skills(self):
        """Retrieve the skill data that will be used to build the response."""
        self._get_available_skills()
        # if self.authenticated:
        #     self._get_skill_manifests()

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

    def _get_skill_manifests(self):
        service_response = call_skill_manifest_endpoint(
            self.tartarus_token,
            self.config['TARTARUS_BASE_URL'],
            self.user_uuid
        )
        if service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(service_response)
        self.skills_in_manifest = parse_skill_manifest_response(
            service_response
        )

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
                search_term in skill.summary.lower()
            )
            if skill.categories and not search_term_match:
                search_term_match = (
                    search_term in skill.categories[0].lower()
                )
            for trigger in skill.triggers:
                if search_term in trigger.lower():
                    search_term_match = True
            if search_term_match:
                skills_to_include.append(skill)

        return skills_to_include

    def _reformat_skills(self, skills_to_include: list):
        """Build the response data from the skill service response"""
        for skill in skills_to_include:
            install_status = None
            manifest_skills = self.skills_in_manifests.get(skill.skill_name)
            if skill.marketplace_category == SYSTEM_CATEGORY:
                install_status = SYSTEM_CATEGORY.lower()
            elif manifest_skills is not None:
                aggregated_manifest = aggregate_manifest_skills(manifest_skills)
                install_status = aggregated_manifest.installation

            skill_summary = dict(
                credits=skill.credits,
                icon=skill.icon,
                iconImage=skill.icon_image,
                id=skill.id,
                installStatus=install_status,
                repositoryUrl=skill.repository_url,
                summary=markdown(skill.summary, output_format='html5'),
                title=skill.title,
                triggers=skill.triggers
            )
            self.response_skills[skill.marketplace_category].append(
                skill_summary
            )

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        for skill_category, skills in self.response_skills.items():
            sorted_skills = sorted(skills, key=lambda skill: skill['title'])
            self.response_skills[skill_category] = sorted_skills
