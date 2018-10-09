"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict
from http import HTTPStatus
from logging import getLogger

from markdown import markdown
import requests as service_request

from selene_util.api import SeleneEndpoint, APIError

UNDEFINED = 'Not Categorized'

_log = getLogger(__package__)


class SkillSummaryEndpoint(SeleneEndpoint):
    authentication_required = False

    def __init__(self):
        super(SkillSummaryEndpoint, self).__init__()
        self.available_skills: list = []
        self.installed_skills: list = []
        self.response_skills = defaultdict(list)

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
        self._get_available_skills()
        self._get_installed_skills()

    def _get_available_skills(self):
        skill_service_response = service_request.get(
            self.config['SELENE_BASE_URL'] + '/skill/all'
        )
        if skill_service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(skill_service_response)
        self.available_skills = skill_service_response.json()

    # TODO: this is a temporary measure until skill IDs can be assigned
    # the list of installed skills returned by Tartarus are keyed by a value
    # that is not guaranteed to be the same as the skill title in the skill
    # metadata.  a skill ID needs to be defined and propagated.
    def _get_installed_skills(self):
        """Get the skills a user has already installed on their device(s)

        Installed skills will be marked as such in the marketplace so a user
        knows it is already installed.
        """
        if self.authenticated:
            service_request_headers = {
                'Authorization': 'Bearer ' + self.tartarus_token
            }
            service_url = (
                self.config['TARTARUS_BASE_URL'] +
                '/user/' +
                self.user_uuid +
                '/skill'
            )
            user_service_response = service_request.get(
                service_url,
                headers=service_request_headers
            )
            if user_service_response.status_code != HTTPStatus.OK:
                self._check_for_service_errors(user_service_response)

            response_skills = user_service_response.json()
            for skill in response_skills.get('skills', []):
                self.installed_skills.append(skill['skill']['name'])

    def _build_response_data(self):
        """Build the data to include in the response."""
        if self.request.query_string:
            skills_to_include = self._filter_skills()
        else:
            skills_to_include = self.available_skills
        self._reformat_skills(skills_to_include)
        self._sort_skills()

    def _filter_skills(self) -> list:
        skills_to_include = []

        query_string = self.request.query_string.decode()
        search_term = query_string.lower().split('=')[1]
        for skill in self.available_skills:
            search_term_match = (
                search_term is None or
                search_term in skill['title'].lower() or
                search_term in skill['description'].lower() or
                search_term in skill['summary'].lower()
            )
            if skill['categories'] and not search_term_match:
                search_term_match = (
                    search_term in skill['categories'][0].lower()
                )
            for trigger in skill['triggers']:
                if search_term in trigger.lower():
                    search_term_match = True
            if search_term_match:
                skills_to_include.append(skill)

        return skills_to_include

    def _reformat_skills(self, skills_to_include: list):
        """Build the response data from the skill service response"""
        for skill in skills_to_include:
            if not skill['icon']:
                skill['icon'] = dict(icon='comment-alt', color='#6C7A89')
            skill_summary = dict(
                credits=skill['credits'],
                icon=skill['icon'],
                icon_image=skill.get('icon_image'),
                id=skill['id'],
                installed=skill['title'] in self.installed_skills,
                repository_url=skill['repository_url'],
                summary=markdown(skill['summary'], output_format='html5'),
                title=skill['title'],
                triggers=skill['triggers']
            )
            if 'system' in skill['tags']:
                skill_category = 'System'
            elif skill['categories']:
                # a skill may have many categories.  the first one in the
                # list is considered the "primary" category.  This is the
                # category the marketplace will use to group the skill.
                skill_category = skill['categories'][0]
            else:
                skill_category = UNDEFINED
            self.response_skills[skill_category].append(skill_summary)

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        for skill_category, skills in self.response_skills.items():
            sorted_skills = sorted(skills, key=lambda skill: skill['title'])
            self.response_skills[skill_category] = sorted_skills
