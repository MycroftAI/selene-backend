# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Base class for Flask API endpoints"""
from logging import getLogger

from flask import after_this_request, current_app, request, g as global_context
from flask.views import MethodView

from selene.data.account import Account, AccountRepository
from selene.util.auth import AuthenticationError, AuthenticationToken
from selene.util.db import connect_to_db

ACCESS_TOKEN_COOKIE_NAME = 'seleneAccess'
FIFTEEN_MINUTES = 900
ONE_MONTH = 2628000
REFRESH_TOKEN_COOKIE_NAME = 'seleneRefresh'

_log = getLogger(__package__)


class APIError(Exception):
    """Raise this exception whenever a non-successful response is built"""
    pass


class SeleneEndpoint(MethodView):
    """
    Abstract base class for Selene Flask Restful API calls.

    Subclasses must do the following:
        -  override the allowed_methods class attribute to a list of all allowed
           HTTP methods.  Each list member must be a HTTPMethod enum
        -  override the _build_response_data method
    """
    def __init__(self):
        """
        Initialize a new access token.

        Args:
            self: (todo): write your description
        """
        global_context.url = request.url
        self.config: dict = current_app.config
        self.request = request
        self.response: tuple = None
        self.account: Account = None
        self.access_token = self._init_access_token()
        self.refresh_token = self._init_refresh_token()

    @property
    def db(self):
        """
        Return a global database.

        Args:
            self: (todo): write your description
        """
        if 'db' not in global_context:
            global_context.db = connect_to_db(
                current_app.config['DB_CONNECTION_CONFIG']
            )

        return global_context.db

    def _init_access_token(self):
        """
        Create an access token.

        Args:
            self: (todo): write your description
        """
        return AuthenticationToken(
            self.config['ACCESS_SECRET'],
            FIFTEEN_MINUTES
        )

    def _init_refresh_token(self):
        """
        Create a refresh token.

        Args:
            self: (todo): write your description
        """
        return AuthenticationToken(
            self.config['REFRESH_SECRET'],
            ONE_MONTH
        )

    def _authenticate(self):
        """
        Authenticate the user using tokens passed via cookies.

        :raises: APIError()
        """
        try:
            account_id = self._validate_auth_tokens()
            self._get_account(account_id)
            self._validate_account(account_id)
            if self.access_token.is_expired:
                self._refresh_auth_tokens()
        except Exception:
            _log.exception('an exception occurred during authentication')
            raise

    def _validate_auth_tokens(self):
        """Ensure the tokens are passed in request and are well formed."""
        self._get_auth_tokens()
        self._decode_access_token()
        if self.access_token.is_expired:
            self._decode_refresh_token()
        account_not_found = (
            self.access_token.account_id is None and
            self.refresh_token.account_id is None
        )
        if account_not_found:
            raise AuthenticationError(
                'failed to retrieve account ID from authentication tokens'
            )

        return self.access_token.account_id or self.refresh_token.account_id

    def _get_auth_tokens(self):
        """
        Get the access token from the request.

        Args:
            self: (todo): write your description
        """
        self.access_token.jwt = self.request.cookies.get(
            ACCESS_TOKEN_COOKIE_NAME
        )
        self.refresh_token.jwt = self.request.cookies.get(
            REFRESH_TOKEN_COOKIE_NAME
        )
        if self.access_token.jwt is None and self.refresh_token.jwt is None:
            raise AuthenticationError('no authentication tokens found')

    def _decode_access_token(self):
        """Decode the JWT to get the account ID and check for errors."""
        self.access_token.validate()

        if not self.access_token.is_valid:
            raise AuthenticationError('invalid access token')

    def _decode_refresh_token(self):
        """Decode the JWT to get the account ID and check for errors."""
        self.refresh_token.validate()

        if not self.refresh_token.is_valid:
            raise AuthenticationError('invalid refresh token')

        if self.refresh_token.is_expired:
            raise AuthenticationError('authentication tokens expired')

    def _get_account(self, account_id):
        """Use account ID from decoded authentication token to get account."""
        account_repository = AccountRepository(self.db)
        self.account = account_repository.get_account_by_id(account_id)

    def _validate_account(self, account_id: str):
        """Account must exist and contain have a refresh token matching request.

        :raises: AuthenticationError
        """
        if self.account is None:
            _log.error('account ID {} not on database'.format(account_id))
            raise AuthenticationError('account not found')
        else:
            global_context.account_id = self.account.id

    def _refresh_auth_tokens(self):
        """Steps necessary to refresh the tokens used for authentication."""
        self._generate_tokens()
        self._set_token_cookies()

    def _generate_tokens(self):
        """Generate an access token and refresh token."""
        self.access_token = self._init_access_token()
        self.refresh_token = self._init_refresh_token()
        self.access_token.generate(self.account.id)
        self.refresh_token.generate(self.account.id)

    def _set_token_cookies(self, expire=False):
        """Set the cookies that contain the authentication token.

        This method should be called when a user logs in, logs out, or when
        their access token expires.

        :param expire: generate tokens that immediately expire, effectively
            logging a user out of the system.
        :return:
        """
        access_token_cookie = dict(
            key='seleneAccess',
            value=str(self.access_token.jwt),
            domain=self.config['DOMAIN'],
            max_age=FIFTEEN_MINUTES,
        )
        refresh_token_cookie = dict(
            key='seleneRefresh',
            value=str(self.refresh_token.jwt),
            domain=self.config['DOMAIN'],
            max_age=ONE_MONTH,
        )

        if expire:
            for cookie in (access_token_cookie, refresh_token_cookie):
                cookie.update(value='', max_age=0)

        @after_this_request
        def set_cookies(response):
            """Use Flask after request hook to reset token cookies"""
            response.set_cookie(**access_token_cookie)
            response.set_cookie(**refresh_token_cookie)

            return response
