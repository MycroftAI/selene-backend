"""Authenticate a user logging in with a email address and password

This type of login is considered "internal" because we are storing the email
address and password on our servers.  This is as opposed to "external"
authentication, which uses a 3rd party authentication, like Google.

"""
from binascii import a2b_base64
from http import HTTPStatus
from time import time

from flask import after_this_request

from selene.account import Account, AccountRepository, RefreshTokenRepository
from selene.api import SeleneEndpoint, APIError
from selene.util.auth import (
    AuthenticationError,
    AuthenticationTokenGenerator,
    FIFTEEN_MINUTES,
    ONE_MONTH
)
from selene.util.db import get_db_connection


class AuthenticateInternalEndpoint(SeleneEndpoint):
    """
    Sign in a user with an email address and password.
    """
    def __init__(self):
        super(AuthenticateInternalEndpoint, self).__init__()
        self.response_status_code = HTTPStatus.OK
        self.account: Account = None

    def get(self):
        try:
            self._authenticate_credentials()
            access_token, refresh_token = self._generate_tokens()
            self._add_refresh_token_to_db(refresh_token)
            cookies = self._generate_token_cookies(access_token, refresh_token)
        except APIError:
            pass
        else:
            self._build_response()

        @after_this_request
        def set_cookies(response):
            access_token_cookie, refresh_token_cookie = cookies
            response.set_cookie(**access_token_cookie)
            response.set_cookie(**refresh_token_cookie)
            return response

        return self.response

    def _authenticate_credentials(self):
        """Compare credentials in request to credentials in database."""

        basic_credentials = self.request.headers['authorization']
        binary_credentials = a2b_base64(basic_credentials.strip('Basic '))
        email_address, password = binary_credentials.decode().split(':')
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            auth_repository = AccountRepository(db)
            self.account = auth_repository.get_account_from_credentials(
                    email_address,
                    password
            )
        if self.account is None:
            raise AuthenticationError('provided credentials not found')

    def _add_refresh_token_to_db(self, refresh_token):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repo = RefreshTokenRepository(db, self.account)
            token_repo.add_refresh_token(refresh_token)

    def _build_response(self):
        self.response = ({}, HTTPStatus.OK)
