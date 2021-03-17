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
"""Device API endpoint to send an email as specified by the device."""
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository
from selene.util.email import EmailMessage, SeleneMailer


class SendEmail(Model):
    """Data model of the incoming PUT request."""

    title = StringType(required=True)
    sender = StringType(required=True)
    body = StringType(required=True)


class DeviceEmailEndpoint(PublicEndpoint):
    """Endpoint to send an email to the account associated to a device"""

    def put(self, device_id):
        """Handle an HTTP PUT request."""
        self._authenticate(device_id)
        self._validate_request()
        account = AccountRepository(self.db).get_account_by_device_id(device_id)
        self._send_message(account)

        return "", HTTPStatus.OK

    def _validate_request(self):
        """Validate that the request is well-formed."""
        send_email = SendEmail(self.request.json)
        send_email.validate()

    def _send_message(self, account):
        """Send an email to the account that owns the device that requested it."""
        message = EmailMessage(
            recipient=account.email_address,
            sender=self.request.json["sender"],
            subject=self.request.json["title"],
            body=self.request.json["body"],
        )
        mailer = SeleneMailer(message)
        mailer.send()
