"""View to return detailed information about a skill"""
from markdown import markdown
import requests as service_request

from selene_util.api import SeleneBaseView, AuthorizationError


class SkillDetailView(SeleneBaseView):
    def __init__(self):
        super(SkillDetailView, self).__init__()
        self.skill_id = None

    def get(self, skill_id):
        """Handle and HTTP GET request."""
        self.skill_id = skill_id
        try:
            self._authenticate()
        except AuthorizationError:
            pass
        self._build_response()

        return self.response

    def _build_response_data(self):
        """Build the data to include in the response."""
        self.service_response = service_request.get(
            self.base_url + '/skill/id/' + self.skill_id
        )
        self.response_data = self.service_response.json()
        self.response_data['description'] = markdown(
            self.response_data['description'],
            output_format='html5'
        )
        self.response_data['summary'] = markdown(
            self.response_data['summary'],
            output_format='html5'
        )