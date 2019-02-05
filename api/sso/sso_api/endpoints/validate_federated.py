from http import HTTPStatus
import json

from selene.api import SeleneEndpoint
from selene.account import AccountRepository, RefreshTokenRepository
from selene.util.auth import AuthenticationError
from selene.util.db import get_db_connection


class ValidateFederatedEndpoint(SeleneEndpoint):
    def post(self):
        try:
            self._get_account()
        except AuthenticationError as ae:
            self.response = str(ae), HTTPStatus.UNAUTHORIZED
        else:
            access_token, refresh_token = self._generate_tokens()
            self._generate_token_cookies(access_token, refresh_token)
            self._update_refresh_token_on_db(refresh_token)
            self.response = 'account validated', HTTPStatus.OK

        return self.response

    def _get_account(self):
        request_data = json.loads(self.request.data)
        email_address = request_data['email']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            self.account = acct_repository.get_account_by_email(email_address)

        if self.account is None:
            raise AuthenticationError('account not found')

    def _add_refresh_token_to_db(self, refresh_token):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repo = RefreshTokenRepository(db, self.account)
            token_repo.add_refresh_token(refresh_token)
