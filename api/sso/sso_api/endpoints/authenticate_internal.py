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

"""Authenticate a user logging in with a email address and password

This type of login is considered "internal" because we are storing the email
address and password on our servers.  This is as opposed to "external"
authentication, which uses a 3rd party authentication, like Google.
"""

from binascii import a2b_base64
from http import HTTPStatus

from selene.data.account import Account, AccountRepository
from selene.api import SeleneEndpoint
from selene.util.auth import AuthenticationError


class AuthenticateInternalEndpoint(SeleneEndpoint):
    """Sign in a user with an email address and password."""
    def __init__(self):
        """
        Initialize the account.

        Args:
            self: (todo): write your description
        """
        super(AuthenticateInternalEndpoint, self).__init__()
        self.account: Account = None

    def get(self):
        """Process HTTP GET request."""
        self._authenticate_credentials()
        self._generate_tokens()
        self._set_token_cookies()

        return '', HTTPStatus.NO_CONTENT

    def _authenticate_credentials(self):
        """Compare credentials in request to credentials in database.

        :raises AuthenticationError when no match found on database
        """
        basic_credentials = self.request.headers['authorization']
        binary_credentials = a2b_base64(basic_credentials[6:])
        email_address, password = binary_credentials.decode().split(':||:')
        acct_repository = AccountRepository(self.db)
        self.account = acct_repository.get_account_from_credentials(
                email_address,
                password
        )
        if self.account is None:
            raise AuthenticationError('provided credentials not found')
        self.access_token.account_id = self.account.id
        self.refresh_token.account_id = self.account.id
