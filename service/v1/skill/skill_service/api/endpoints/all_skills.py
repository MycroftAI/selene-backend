"""Define the view to return summary information for all available skills."""

from http import HTTPStatus

from flask_restful import Resource

from .skill_formatter import format_skill_for_response
from ...repository.skill import select_all_skills


class AllSkillsEndpoint(Resource):
    """All skills available for use on devices running Mycroft core."""

    def get(self):
        """Handle a HTTP GET request for available skills."""
        response = []
        for skill in select_all_skills():
            formatted_skill = format_skill_for_response(skill)
            response.append(formatted_skill)

        return response, HTTPStatus.OK
