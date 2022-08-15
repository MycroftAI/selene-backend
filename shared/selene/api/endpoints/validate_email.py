#  Mycroft Server - Backend
#  Copyright (c) 2022 Mycroft AI Inc
#  SPDX-License-Identifier: 	AGPL-3.0-or-later
#  #
#  This file is part of the Mycroft Server.
#  #
#  The Mycroft Server is free software: you can redistribute it and/or
#  modify it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#  #
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Defines an API endpoint to validate an email address supplied by the user."""

from binascii import a2b_base64
from http import HTTPStatus

from selene.api import APIError, SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import (
    get_facebook_account_email,
    get_github_account_email,
    get_google_account_email,
)
from selene.util.email import validate_email_address


class ValidateEmailEndpoint(SeleneEndpoint):
    """Defines an API endpoint to validate an email address supplied by the user."""

    def get(self):
        """Handles a HTTP GET request."""
        return_data = dict(accountExists=False, noFederatedEmail=False)
        if self.request.args["token"]:
            email_address = self._get_email_address()
            if self.request.args["platform"] != "Internal" and not email_address:
                return_data.update(noFederatedEmail=True)
            account_repository = AccountRepository(self.db)
            account = account_repository.get_account_by_email(email_address)
            if account is not None:
                return_data.update(accountExists=True)

        return return_data, HTTPStatus.OK

    def _get_email_address(self):
        """Retrieves the user's email address from the URL or service provider."""
        if self.request.args["platform"] == "Google":
            email_address = get_google_account_email(self.request.args["token"])
        elif self.request.args["platform"] == "Facebook":
            email_address = get_facebook_account_email(self.request.args["token"])
        elif self.request.args["platform"] == "GitHub":
            email_address = get_github_account_email(self.request.args["token"])
        else:
            email_address = self._validate_email_address()

        return email_address

    def _validate_email_address(self) -> str:
        """Validates the user's email address to ensure notifications can be sent."""
        coded_email = self.request.args["token"]
        email_address = a2b_base64(coded_email).decode()
        normalized_email_address, error = validate_email_address(email_address)
        if error is not None:
            raise APIError(error)

        return normalized_email_address
