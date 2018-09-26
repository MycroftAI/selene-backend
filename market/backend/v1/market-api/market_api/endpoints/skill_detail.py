"""View to return detailed information about a skill"""
from http import HTTPStatus

from markdown import markdown
import requests as service_request

from selene_util.api import SeleneBaseView, APIError, HTTPMethod


class SkillDetailView(SeleneBaseView):
    allowed_methods = [HTTPMethod.GET]

    def __init__(self):
        super(SkillDetailView, self).__init__()
        self.skill_id = None

    def get(self, skill_id):
        self.skill_id = skill_id
        response = super(SkillDetailView, self).get()
        return response

    def _authenticate(self):
        """Override the default behavior of requiring authentication

        The marketplace is viewable without authenticating.  Installing a
        skill requires authentication though.
        """
        try:
            super(SkillDetailView, self)._authenticate()
        except APIError:
            self.response_status = HTTPStatus.OK
            self.response_error_message = None
        else:
            self.user_is_authenticated = True

    def _get_requested_data(self):
        """Build the data to include in the response."""
        skill_service_response = service_request.get(
            self.base_url + '/skill/id/' + self.skill_id
        )
        self._check_for_service_errors(skill_service_response)
        self.response_data = skill_service_response.json()

    def _build_response_data(self):
        self.response_data['description'] = markdown(
            self.response_data['description'],
            output_format='html5'
        )
        self.response_data['summary'] = markdown(
            self.response_data['summary'],
            output_format='html5'
        )