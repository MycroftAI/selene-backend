from http import HTTPStatus

from selene_util.api import SeleneEndpoint
from selene_util.auth import encode_auth_token, THIRTY_DAYS
from time import time
import json

class AuthenticateSocialEndpoint(SeleneEndpoint):
    def __init__(self):
        super(AuthenticateSocialEndpoint, self).__init__()
        self.response_status_code = HTTPStatus.OK
        self.tartarus_token = None
        self.users_uuid = None

    def get(self):
        self._get_tartarus_token()
        self._build_front_end_response()
        return self.response

    def _get_tartarus_token(self):
        args = self.request.args
        if "data" in args:
            self.tartarus_token = args['data']
            token_json = json.loads(self.tartarus_token)
            self.users_uuid = token_json["uuid"]

    def _build_front_end_response(self):
        self.selene_token = encode_auth_token(
            self.config['SECRET_KEY'], self.users_uuid
        )

        response_data = dict(
            expiration=time() + THIRTY_DAYS,
            seleneToken=self.selene_token,
            tartarusToken=self.tartarus_token,
        )
        self.response = (response_data, HTTPStatus.OK)