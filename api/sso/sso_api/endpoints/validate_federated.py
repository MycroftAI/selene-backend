"""Validate user who logged in using a 3rd party authentication mechanism

Authenticating with Google, Faceboook, etc. is known as "federated" login.
Users that choose this option have been authenticated by the selected platform
so all we need to to to complete login is validate that the email address exists
on our database and build JWTs for access and refresh.
"""
from http import HTTPStatus
from logging import getLogger

from facebook import GraphAPI
from flask import json
import requests

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository, RefreshTokenRepository
from selene.util.auth import AuthenticationError
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
        self._add_refresh_token_to_db()
        self.response = dict(result='account validated'), HTTPStatus.OK

        return self.response

    def _get_email_address(self):
        request_data = json.loads(self.request.data)
        if request_data['platform'] == 'Google':
            self._get_email_from_google(request_data['token'])
        elif request_data['platform'] == 'Facebook':
            self._get_email_from_facebook(request_data['token'])

    def _get_email_from_google(self, token):
        google_response = requests.get(
            'https://oauth2.googleapis.com/tokeninfo?id_token=' + token
        )
        if google_response.status_code == HTTPStatus.OK:
            google_account = json.loads(google_response.content)
            self.email_address = google_account['email']
        else:
            raise AuthenticationError('invalid Google token')

    def _get_email_from_facebook(self, token):
        facebook_api = GraphAPI(token)
        facebook_account = facebook_api.get_object(id='me?fields=email')
        self.email_address = facebook_account['email']

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

    def _add_refresh_token_to_db(self):
        """Track refresh tokens in the database.

        We need to store the value of the refresh token in the database so
        that we can validate it when it is used to request new tokens.

        """
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repo = RefreshTokenRepository(db, self.account.id)
            token_repo.add_refresh_token(self.refresh_token.jwt)
