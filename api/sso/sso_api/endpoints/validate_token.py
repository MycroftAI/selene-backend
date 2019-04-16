from http import HTTPStatus
from selene.api import SeleneEndpoint
from selene.util.auth import AuthenticationError, AuthenticationToken


class ValidateTokenEndpoint(SeleneEndpoint):
    def post(self):
        response_data = self._validate_token()
        return response_data, HTTPStatus.OK

    def _validate_token(self):
        auth_token = AuthenticationToken(
            self.config['RESET_SECRET'],
            duration=0
        )
        auth_token.jwt = self.request.json['token']
        auth_token.validate()

        return dict(
            account_id=auth_token.account_id,
            token_expired=auth_token.is_expired,
            token_invalid=not auth_token.is_valid
        )
