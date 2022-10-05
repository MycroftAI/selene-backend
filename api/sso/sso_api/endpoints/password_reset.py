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
"""Single Sign On API endpoint to reset a user's password."""
from http import HTTPStatus
import os

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import AuthenticationToken
from selene.util.email import EmailMessage, SeleneMailer

ONE_HOUR = 3600


class PasswordResetEndpoint(SeleneEndpoint):
    """Defines an endpoint that will be called when a user resets their password."""

    def post(self):
        """Handles an HTTP POST request."""
        self._get_account_from_email()
        if self.account is None:
            self._send_account_not_found_email()
        else:
            reset_token = self._generate_reset_token()
            self._send_reset_email(reset_token)

        return "", HTTPStatus.OK

    def _get_account_from_email(self):
        """Retrieves the account from the database using the email address on the db."""
        acct_repository = AccountRepository(self.db)
        self.account = acct_repository.get_account_by_email(
            self.request.json["emailAddress"]
        )

    def _generate_reset_token(self) -> str:
        """Returns a reset token that will be included in the password reset email."""
        reset_token = AuthenticationToken(self.config["RESET_SECRET"], ONE_HOUR)
        reset_token.generate(self.account.id)

        return reset_token.jwt

    def _send_reset_email(self, reset_token: str):
        """Sends a password reset message to the email address provided by the user.

        :param reset_token: JWT to authenticate the password reset
        """
        url = f"{os.environ['SSO_BASE_URL']}/change-password?token={reset_token}"
        email = EmailMessage(
            recipient=self.request.json["emailAddress"],
            sender="Mycroft AI<no-reply@mycroft.ai>",
            subject="Password Reset Request",
            template_file_name="reset_password.html",
            template_variables=dict(reset_password_url=url),
        )
        mailer = SeleneMailer(email)
        mailer.send(using_jinja=True)

    def _send_account_not_found_email(self):
        """Sends an email indicating no account found for supplied email address."""
        email = EmailMessage(
            recipient=self.request.json["emailAddress"],
            sender="Mycroft AI<no-reply@mycroft.ai>",
            subject="Password Reset Request",
            template_file_name="account_not_found.html",
        )
        mailer = SeleneMailer(email)
        mailer.send()
