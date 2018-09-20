"""Endpoint to provide skill summary data to the marketplace."""
from collections import defaultdict

from flask import request, current_app
from markdown import markdown
import requests as service_request

from selene_util.api import SeleneBaseView, AuthorizationError

UNDEFINED = 'Undefined'


class SkillSummaryView(SeleneBaseView):
    allowed_methods = 'GET'

    def __init__(self):
        super(SkillSummaryView, self).__init__()
        self.response_data = defaultdict(list)
        self.skill_service_response = None

    def get(self):
        """Handle a HTTP GET request."""
        try:
            self._authenticate()
        except AuthorizationError:
            # it's okay if user is not authenticated, they just won't be able
            # to install any skills
            pass
        self._build_response()

        return self.response

    def _build_response_data(self):
        """Build the data to include in the response."""
        self._get_available_skills()
        installed_skills = self._get_installed_skills()
        skills_to_include = self._filter_skills()
        self._reformat_skills(skills_to_include, installed_skills)
        self._sort_skills()

    def _get_available_skills(self):
        self.skill_service_response = service_request.get(
            self.base_url + '/skill/all'
        )

    def _get_installed_skills(self) -> list:
        """Get the skills a user has already installed on their device(s)

        Installed skills will be marked as such in the marketplace so a user
        knows it is already installed.
        """
        installed_skills = []
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
            # self.check_for_tartarus_errors(service_url)
            response_skills = user_service_response.json()
            for skill in response_skills['skills']:
                installed_skills.append(skill['skill']['name'])

        return installed_skills

    def _filter_skills(self) -> list:
        skills_to_include = []
        search_term = None
        if request.query_string:
            query_string = request.query_string.decode()
            search_term = query_string.lower().split('=')[1]
        for skill in self.skill_service_response.json():
            search_term_match = (
                search_term is None or
                search_term in skill['title'].lower()
            )
            if search_term_match:
                skills_to_include.append(skill)

        return skills_to_include

    def _reformat_skills(self, skills_to_include: list, installed_skills: list):
        """Build the response data from the skill service response"""
        for skill in skills_to_include:
            if not skill['icon']:
                skill['icon'] = dict(icon='comment-alt', color='#6C7A89')
            skill_summary = dict(
                credits=skill['credits'],
                icon=skill['icon'],
                icon_image=skill.get('icon_image'),
                id=skill['id'],
                installed=skill['title'] in installed_skills,
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
