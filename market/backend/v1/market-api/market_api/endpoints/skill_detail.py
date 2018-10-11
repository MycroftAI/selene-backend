"""View to return detailed information about a skill"""
from http import HTTPStatus

from markdown import markdown
import requests as service_request

from .common import SkillEndpointBase
from selene_util.api import APIError


class SkillDetailEndpoint(SkillEndpointBase):
    """"Supply the data that will populate the skill detail page."""
    authentication_required = False

    def __init__(self):
        super(SkillDetailEndpoint, self).__init__()
        self.skill_id = None
        self.response_skill = None

    def get(self, skill_id):
        """Process an HTTP GET request"""
        self.skill_id = skill_id
        try:
            self._authenticate()
            self._get_skill_details()
            self._get_skill_manifests()
        except APIError:
            pass
        else:
            self._build_response_data()
            self.response = (self.response_skill, HTTPStatus.OK)

        return self.response

    def _get_skill_details(self):
        """Build the data to include in the response."""
        skill_service_response = service_request.get(
            self.config['SELENE_BASE_URL'] + '/skill/id/' + self.skill_id
        )
        self._check_for_service_errors(skill_service_response)
        self.response_skill = skill_service_response.json()

    def _build_response_data(self):
        """Make some modifications to the response skill for the marketplace"""
        install_status = self._determine_skill_install_status(
            self.response_skill
        )
        is_installed, is_installing, install_failed = install_status
        self.response_skill.update(
            description=markdown(
                self.response_skill['description'],
                output_format='html5'
            ),
            summary=markdown(
                self.response_skill['summary'],
                output_format='html5'
            ),
            is_installed=is_installed,
            is_installing=is_installing,
            install_failed=install_failed
        )
