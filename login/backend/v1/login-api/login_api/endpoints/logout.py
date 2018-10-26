"""Log a user out of Mycroft web sites"""

from http import HTTPStatus
from logging import getLogger

import requests

from selene_util.api import SeleneEndpoint, APIError

_log = getLogger(__package__)


class LogoutEndpoint(SeleneEndpoint):
    def __init__(self):
        super(LogoutEndpoint, self).__init__()

    def get(self):
        try:
            self._authenticate()
            self._logout()
        except APIError:
            pass

        return self.response

    def _logout(self):
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = self.config['TARTARUS_BASE_URL'] + '/auth/logout'
        auth_service_response = requests.get(
            service_url,
            headers=service_request_headers
        )
        self._check_for_service_errors(auth_service_response)
        logout_response = auth_service_response.json()
        self.response = (logout_response, HTTPStatus.OK)
