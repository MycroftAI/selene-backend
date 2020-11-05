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

"""Validate user who logged in using a 3rd party authentication mechanism

Authenticating with Google, Faceboook, etc. is known as "federated" login.
Users that choose this option have been authenticated by the selected platform
so all we need to to to complete login is validate that the email address exists
on our database and build JWTs for access and refresh.
"""
from http import HTTPStatus
from logging import getLogger

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import (
    AuthenticationError,
    get_facebook_account_email,
    get_google_account_email,
    get_github_account_email
)

FEDERATED_PLATFORMS = ('Facebook', 'Google', 'GitHub')

_log = getLogger()


class ValidateFederatedRequest(Model):
    platform = StringType(required=True, choices=FEDERATED_PLATFORMS)
    token = StringType(required=True)


class ValidateFederatedEndpoint(SeleneEndpoint):
    def __init__(self):
        """
        Initialize the email_address.

        Args:
            self: (todo): write your description
        """
        super(ValidateFederatedEndpoint, self).__init__()
        self.email_address = None

    def post(self):
        """Process a HTTP POST request."""
        self._validate_request()
        self._get_email_address()
        self._get_account_by_email()
        self._generate_tokens()
        self._set_token_cookies()

        return '', HTTPStatus.NO_CONTENT

    def _validate_request(self):
        """
        Validate the request.

        Args:
            self: (todo): write your description
        """
        validator = ValidateFederatedRequest(self.request.json)
        validator.validate()

    def _get_email_address(self):
        """
        Get the email address for the account.

        Args:
            self: (todo): write your description
        """
        if self.request.json['platform'] == 'Google':
            self.email_address = get_google_account_email(
                self.request.json['token']
            )
        elif self.request.json['platform'] == 'Facebook':
            self.email_address = get_facebook_account_email(
                self.request.json['token']
            )
        elif self.request.json['platform'] == 'GitHub':
            self.email_address = get_github_account_email(
                self.request.json['token']
            )

    def _get_account_by_email(self):
        """Use email returned by the authentication platform for validation"""
        if self.email_address is None:
            raise AuthenticationError('could not retrieve email from provider')

        acct_repository = AccountRepository(self.db)
        self.account = acct_repository.get_account_by_email(
            self.email_address
        )

        if self.account is None:
            raise AuthenticationError('no account found for provided email')
