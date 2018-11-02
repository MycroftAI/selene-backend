"""View to return detailed information about a skill"""
from http import HTTPStatus

from markdown import markdown
import requests as service_request

from selene_util.api import APIError, SeleneEndpoint
from .common import RepositorySkill


class SkillDetailEndpoint(SeleneEndpoint):
    """"Supply the data that will populate the skill detail page."""
    authentication_required = False

    def __init__(self):
        super(SkillDetailEndpoint, self).__init__()
        self.skill_name = None
        self.response_skill = None
        self.manifest_skills = []

    def get(self, skill_name):
        """Process an HTTP GET request"""
        self.skill_name = skill_name
        try:
            repository_skill = self._get_skill_details()
        except APIError:
            pass
        else:
            self._build_response_data(repository_skill)
            self.response = (self.response_skill, HTTPStatus.OK)

        return self.response

    def _get_skill_details(self) -> RepositorySkill:
        """Build the data to include in the response."""
        skill_service_response = service_request.get(
            self.config['SELENE_BASE_URL'] + '/skill/name/' + self.skill_name
        )
        self._check_for_service_errors(skill_service_response)

        service_response = skill_service_response.json()
        repository_skill = RepositorySkill(**service_response)

        return repository_skill

    def _build_response_data(self, repository_skill: RepositorySkill):
        """Make some modifications to the response skill for the marketplace"""
        self.response_skill = dict(
            categories=repository_skill.categories,
            credits=repository_skill.credits,
            description=markdown(
                repository_skill.description,
                output_format='html5'
            ),
            icon=repository_skill.icon,
            iconImage=repository_skill.icon_image,
            isSystemSkill=repository_skill.is_system_skill,
            name=repository_skill.skill_name,
            worksOnMarkOne=(
                'all' in repository_skill.platforms or
                'platform_mark1' in repository_skill.platforms
            ),
            worksOnMarkTwo=(
                'all' in repository_skill.platforms or
                'platform_mark2' in repository_skill.platforms
            ),
            worksOnPicroft=(
                'all' in repository_skill.platforms or
                'platform_picroft' in repository_skill.platforms
            ),
            worksOnKDE=(
                'all' in repository_skill.platforms or
                'platform_plasmoid' in repository_skill.platforms
            ),
            repositoryUrl=repository_skill.repository_url,
            summary=markdown(
                repository_skill.summary,
                output_format='html5'
            ),
            title=repository_skill.title,
            triggers=repository_skill.triggers
        )
