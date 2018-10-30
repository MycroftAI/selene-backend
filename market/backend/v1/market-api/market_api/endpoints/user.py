"""API endpoint to return the user's name to the marketplace"""
from http import HTTPStatus

import requests

from selene_util.api import SeleneEndpoint, APIError


class UserEndpoint(SeleneEndpoint):
    """Retrieve information about the user based on their UUID"""
    def __init__(self):
        super(UserEndpoint, self).__init__()
        self.user = None
        self.frontend_response = None

    def get(self):
        """Process HTTP GET request for a user."""
        try:
            self._authenticate()
            self._get_user()
        except APIError:
            pass
        else:
            self._build_response()

        return self.response

    def _get_user(self):
        """Call the Tartarus endpoint for retrieving user information."""
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
            self.config['TARTARUS_BASE_URL'] +
            '/user/' +
            self.user_uuid
        )
        user_service_response = requests.get(
            service_url,
            headers=service_request_headers
        )
        self._check_for_service_errors(user_service_response)
        self.user = user_service_response.json()

    def _build_response(self):
        """Build the response to the user info request."""
        response_data = dict(name=self.user.get('name'))
        self.response = (response_data, HTTPStatus.OK)
