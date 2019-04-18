"""Validate user who logged in using a 3rd party authentication mechanism

Authenticating with Google, Faceboook, etc. is known as "federated" login.
Users that choose this option have been authenticated by the selected platform
so all we need to to to complete login is validate that the email address exists
on our database and build JWTs for access and refresh.
"""
from http import HTTPStatus
from logging import getLogger

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import (
    AuthenticationError,
    get_facebook_account_email,
    get_google_account_email
)
from selene.util.db import get_db_connection

_log = getLogger()


class ValidateFederatedEndpoint(SeleneEndpoint):
    def __init__(self):
        super(ValidateFederatedEndpoint, self).__init__()
        self.email_address = None

    def post(self):
        """Process a HTTP POST request."""
        self._get_email_address()
        self._get_account_by_email()
        self._generate_tokens()
        self._set_token_cookies()
        self.response = dict(result='account validated'), HTTPStatus.OK

        return self.response

    def _get_email_address(self):
        if self.request.json['platform'] == 'Google':
            self.email_address = get_google_account_email(
                self.request.json['token']
            )
        elif self.request.json['platform'] == 'Facebook':
            self.email_address = get_facebook_account_email(
                self.request.json['token']
            )

    def _get_account_by_email(self):
        """Use email returned by the authentication platform for validation"""
        if self.email_address is None:
            raise AuthenticationError('could not retrieve email from provider')

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            self.account = acct_repository.get_account_by_email(
                self.email_address
            )

        if self.account is None:
            raise AuthenticationError('no account found for provided email')
