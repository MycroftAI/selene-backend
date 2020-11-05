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

import json
import os
import smtplib
from email.message import EmailMessage
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class SendEmail(Model):
    title = StringType(required=True)
    sender = StringType(required=True)
    body = StringType(required=True)


class DeviceEmailEndpoint(PublicEndpoint):
    """Endpoint to send an email to the account associated to a device"""

    def __init__(self):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
        """
        super(DeviceEmailEndpoint, self).__init__()

    def put(self, device_id):
        """
        Sends a new account.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        send_email = SendEmail(payload)
        send_email.validate()

        account = AccountRepository(self.db).get_account_by_device_id(device_id)

        if account:
            message = EmailMessage()
            message['Subject'] = str(send_email.title)
            message['From'] = str(send_email.sender)
            message.set_content(str(send_email.body))
            message['To'] = account.email_address
            self._send_email(message)
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def _send_email(self, message: EmailMessage):
        """
        Sends email.

        Args:
            self: (str): write your description
            message: (str): write your description
        """
        email_client = self.config.get('EMAIL_CLIENT')
        if email_client is None:
            host = os.environ['EMAIL_SERVICE_HOST']
            port = os.environ['EMAIL_SERVICE_PORT']
            user = os.environ['EMAIL_SERVICE_USER']
            password = os.environ['EMAIL_SERVICE_PASSWORD']
            email_client = smtplib.SMTP(host, port)
            email_client.login(user, password)
        email_client.send_message(message)
        email_client.quit()
