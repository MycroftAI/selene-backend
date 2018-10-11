"""View to return detailed information about a skill"""
from http import HTTPStatus

from markdown import markdown
import requests as service_request

from .common import (
    aggregate_manifest_skills,
    call_skill_manifest_endpoint,
    parse_skill_manifest_response
)
from selene_util.api import APIError, SeleneEndpoint


class SkillDetailEndpoint(SeleneEndpoint):
    """"Supply the data that will populate the skill detail page."""
    authentication_required = False

    def __init__(self):
        super(SkillDetailEndpoint, self).__init__()
        self.skill_id = None
        self.response_skill = None
        self.manifest_skills = []

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

    def _get_skill_manifests(self):
        service_response = call_skill_manifest_endpoint(
            self.tartarus_token,
            self.config['TARTARUS_BASE_URL'],
            self.user_uuid
        )
        if service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(service_response)
        skills_in_manifest = parse_skill_manifest_response(
            service_response
        )
        self.manifest_skills = skills_in_manifest[
            self.response_skill['skill_name']
        ]

    def _build_response_data(self):
        """Make some modifications to the response skill for the marketplace"""
        aggregated_manifest_skill = aggregate_manifest_skills(
            self.manifest_skills
        )
        self.response_skill.update(
            description=markdown(
                self.response_skill['description'],
                output_format='html5'
            ),
            summary=markdown(
                self.response_skill['summary'],
                output_format='html5'
            ),
            installStatus=aggregated_manifest_skill.installation,
            repositoryUrl=self.response_skill['repository_url'],
            iconImage=self.response_skill['icon_image']
        )

        del(self.response_skill['repository_url'])
        del(self.response_skill['icon_image'])
