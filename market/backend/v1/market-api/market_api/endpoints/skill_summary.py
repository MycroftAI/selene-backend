"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict
from http import HTTPStatus
from logging import getLogger

from flask import request, current_app
from markdown import markdown
import requests as service_request

from selene_util.api import SeleneBaseView, APIError, HTTPMethod

UNDEFINED = 'Undefined'

_log = getLogger(__package__)


class SkillSummaryView(SeleneBaseView):
    allowed_methods = [HTTPMethod.GET]

    def __init__(self):
        super(SkillSummaryView, self).__init__()
        self.available_skills = []
        self.installed_skills = []
        self.response_data = defaultdict(list)
        self.user_is_authenticated: bool = False

    def _authenticate(self):
        """Override the default behavior of requiring authentication

        The marketplace is viewable without authenticating.  Installing a
        skill requires authentication though.
        """
        try:
            super(SkillSummaryView, self)._authenticate()
        except APIError:
            self.response_status = HTTPStatus.OK
            self.response_error_message = None
        else:
            self.user_is_authenticated = True

    def _get_requested_data(self):
        self._get_available_skills()
        self._get_installed_skills()

    def _build_response_data(self):
        """Build the data to include in the response."""
        skills_to_include = self._filter_skills()
        self._reformat_skills(skills_to_include)
        self._sort_skills()

    def _get_available_skills(self):
        skill_service_response = service_request.get(
            self.base_url + '/skill/all'
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
        if self.user_is_authenticated:
            service_request_headers = {
                'Authorization': 'Bearer ' + self.tartarus_token
            }
            service_url = (
                current_app.config['TARTARUS_BASE_URL'] +
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
            if user_service_response.status_code == HTTPStatus.UNAUTHORIZED:
                # override response built in _build_service_error_response()
                # so that user knows there is a authentication issue
                self.response = (self.response[0], HTTPStatus.UNAUTHORIZED)
                raise APIError()

            response_skills = user_service_response.json()
            for skill in response_skills['skills']:
                self.installed_skills.append(skill['skill']['name'])

    def _filter_skills(self) -> list:
        skills_to_include = []
        search_term = None
        if request.query_string:
            query_string = request.query_string.decode()
            search_term = query_string.lower().split('=')[1]
        for skill in self.available_skills:
            search_term_match = (
                search_term is None or
                search_term in skill['title'].lower()
            )
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
                summary=markdown(skill['summary'], output_format='html5'),
                title=skill['title'],
                triggers=skill['triggers']
            )
            # a skill may have many categories.  the first one in the
            # list is considered the "primary" category.  This is the
            # category the marketplace will use to group the skill.
            if skill['categories']:
                skill_category = skill['categories'][0]
            else:
                skill_category = UNDEFINED
            self.response_data[skill_category].append(skill_summary)

    def _sort_skills(self):
        """Sort the skills in alphabetical order"""
        for skill_category, skills in self.response_data.items():
            sorted_skills = sorted(skills, key=lambda skill: skill['title'])
            self.response_data[skill_category] = sorted_skills
