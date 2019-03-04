"""Define the view to get the detailed information about a particular skill."""
from http import HTTPStatus

from flask_restful import Resource

from .skill_formatter import format_skill_for_response
from ...repository.skill import select_skill_by_name


class SkillDetailEndpoint(Resource):
    def get(self, skill_name):
        """Handle HTP GET request for detailed information about a skill."""
        skill = select_skill_by_name(skill_name)
        response = format_skill_for_response(skill)

        return response, HTTPStatus.OK
