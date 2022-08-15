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
"""Defines the password change endpoint for the account API.

This endpoint does not update the email address in the database.  The user needs to
verify the email address is correct before the change is applied.  See the
verify_email_address module in this package for the verification step.
"""
from binascii import a2b_base64, b2a_base64
from http import HTTPStatus
from os import environ

from selene.api import APIError, SeleneEndpoint
from selene.util.email import EmailMessage, SeleneMailer, validate_email_address


class EmailAddressChangeEndpoint(SeleneEndpoint):
    """Adds authentication to the common password changing endpoint."""

    def put(self):
        """Executes an HTTP PUT request."""
        self._authenticate()
        new_email_address = self._validate_request()
        self._send_notification()
        self._send_verification_email(new_email_address)

        return "", HTTPStatus.NO_CONTENT

    def _validate_request(self) -> str:
        """Validates the content of the API request.

        :returns: A validated and normalized email address
        :raises: APIError when email address is invalid
        """
        request_token = self.request.json["token"]
        new_email_address = a2b_base64(request_token).decode()
        normalized_address, error = validate_email_address(new_email_address)
        if error is not None:
            raise APIError(error)

        return normalized_address

    def _send_notification(self):
        """Notifies the current email address' owner of the requested change."""
        _, error = validate_email_address(self.account.email_address)
        if error is None:
            email = EmailMessage(
                recipient=self.account.email_address,
                sender="Mycroft AI<no-reply@mycroft.ai>",
                subject="Email Address Changed",
                template_file_name="email_change.html",
            )
            mailer = SeleneMailer(email)
            mailer.send(using_jinja=True)

    @staticmethod
    def _send_verification_email(new_email_address):
        """Sends an email with a link for email verification to the requested address.

        :param new_email_address: the recipient of the verification email
        """
        base_url = environ["ACCOUNT_BASE_URL"]
        token = b2a_base64(new_email_address.encode(), newline=False).decode()
        url = f"{base_url}/verify-email?token={token}"
        email = EmailMessage(
            recipient=new_email_address,
            sender="Mycroft AI<no-reply@mycroft.ai>",
            subject="Email Change Verification",
            template_file_name="email_verification.html",
            template_variables=dict(email_verification_url=url),
        )
        mailer = SeleneMailer(email)
        mailer.send(using_jinja=True)
