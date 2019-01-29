from http import HTTPStatus
import json
from time import time

from selene.util.api import SeleneEndpoint
from selene.util.auth import encode_auth_token, ONE_DAY


class SocialLoginTokensEndpoint(SeleneEndpoint):
    def post(self):
        self._get_tartarus_token()
        self._build_selene_token()
        self._build_response()
        return self.response

    def _get_tartarus_token(self):
        request_data = json.loads(self.request.data)
        self.tartarus_token = request_data['accessToken']
        self.user_uuid = request_data["uuid"]

    def _build_selene_token(self):
        self.selene_token = encode_auth_token(
            self.config['SECRET_KEY'], self.user_uuid
        )

    def _build_response(self):
        response_data = dict(
            expiration=time() + ONE_DAY,
            seleneToken=self.selene_token,
            tartarusToken=self.tartarus_token,
        )
        self.response = (response_data, HTTPStatus.OK)
