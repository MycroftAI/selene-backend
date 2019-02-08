"""API endpoint to return the a logged-in user's profile"""
from dataclasses import asdict
from http import HTTPStatus

from .base_endpoint import SeleneEndpoint


class AccountEndpoint(SeleneEndpoint):
    """Retrieve information about the user based on their UUID"""

    def get(self):
        """Process HTTP GET request for an account."""
        self._authenticate()
        if self.authenticated:
            self._build_response()

        return self.response

    def _build_response(self):
        """Build the response to the user info request."""
        response_data = asdict(self.account)
        del(response_data['refresh_tokens'])
        self.response = (response_data, HTTPStatus.OK)
