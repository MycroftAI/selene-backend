from http import HTTPStatus
import json
from time import time

import requests as service_request

from selene_util.api import SeleneEndpoint, APIError
from selene_util.auth import encode_auth_token, ONE_DAY


class AuthenticateAntisocialEndpoint(SeleneEndpoint):
    """
    User Login Resource
    """
    def __init__(self):
        super(AuthenticateAntisocialEndpoint, self).__init__()
        self.response_status_code = HTTPStatus.OK
        self.tartarus_token = None
        self.users_uuid = None

    def get(self):
        try:
            self._authenticate_credentials()
        except APIError:
            pass
        else:
            self._build_response()

        return self.response

    def _authenticate_credentials(self):
        basic_credentials = self.request.headers['authorization']
        service_request_headers = {'Authorization': basic_credentials}
        auth_service_response = service_request.get(
            self.config['TARTARUS_BASE_URL'] + '/auth/login',
            headers=service_request_headers
        )
        self._check_for_service_errors(auth_service_response)
        auth_service_response_content = json.loads(
            auth_service_response.content
        )
        self.users_uuid = auth_service_response_content['uuid']
        self.tartarus_token = auth_service_response_content['accessToken']

    def _build_response(self):
        self.selene_token = encode_auth_token(
            self.config['SECRET_KEY'], self.users_uuid
        )
        response_data = dict(
            expiration=time() + ONE_DAY,
            seleneToken=self.selene_token,
            tartarusToken=self.tartarus_token,
        )
        self.response = (response_data, HTTPStatus.OK)