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
"""Account API endpoint to be called when a user is verifying their email address."""

from binascii import a2b_base64
from http import HTTPStatus

from selene.api import SeleneEndpoint, APIError
from selene.data.account import AccountRepository
from selene.util.email import validate_email_address


class VerifyEmailAddressEndpoint(SeleneEndpoint):
    """Updates a user's email address after they have verified it."""

    def put(self):
        """Processes an HTTP PUT request to update the email address."""
        self._authenticate()
        email_address = self._validate_email_address()
        self._update_account(email_address)

        return "", HTTPStatus.NO_CONTENT

    def _validate_email_address(self) -> str:
        """Validates that the email address is well formatted and reachable.

        By this point in the email address change process, this validation has
        already been done.  It is done again here as a protection against malicious
        calls to this endpoint.

        :returns: a normalized version of the email address in the request
        :raises: an API error if the email address validation fails
        """
        encoded_email_address = self.request.json["token"]
        email_address = a2b_base64(encoded_email_address).decode()
        normalized_email_address, error = validate_email_address(email_address)
        if error is not None:
            raise APIError(f"invalid email address: {error}")

        return normalized_email_address

    def _update_account(self, email_address: str):
        """Updates the email address on the DB now that it has been verified.

        :param email_address: the email address to apply to the account.account table
        """
        account_repo = AccountRepository(self.db)
        account_repo.update_email_address(self.account.id, email_address)
