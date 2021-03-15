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
"""Step functions for the device API call to send an email."""
import json
import uuid
from unittest.mock import patch, MagicMock

from behave import when, then  # pylint: disable=no-name-in-module


@when("a user interaction with a device causes an email to be sent")
def send_email(context):
    """Call the email endpoint to send an email as specified by a device.

    The SendGrid call to send email is mocked out because we trust that the library
    is coded to correctly send email via sendgrid.  That, and testing sent emails is
    a real pain in the arse.
    """
    with patch("selene.util.email.email.Mail") as message_patch:
        context.message_patch = message_patch
        with patch("selene.util.email.email.SendGridAPIClient") as sendgrid_patch:
            sendgrid_patch.return_value, post_mock = _define_sendgrid_mock()
            context.sendgrid_patch = sendgrid_patch
            context.post_mock = post_mock
            _call_email_endpoint(context)


@when("an unpaired or unauthenticated device attempts to send an email")
def send_email_invalid_device(context):
    """Call the email endpoint with an invalid device ID to test authentication."""
    _call_email_endpoint(context, device_id=str(uuid.uuid4()))


def _define_sendgrid_mock():
    """Go through some insane hoops to setup the correct Mock for the Sendgrid code."""
    post_return_value = MagicMock(name="post_return")
    post_return_value.status_code = 200
    post_mock = MagicMock(name="post_mock")
    post_mock.return_value = post_return_value
    send_mock = MagicMock(name="send_mock")
    send_mock.post = post_mock
    mail_mock = MagicMock(name="mail_mock")
    mail_mock.send = send_mock
    client_mock = MagicMock(name="client_mock")
    client_mock.mail = mail_mock
    sendgrid_mock = MagicMock(name="sendgrid_mock")
    sendgrid_mock.client = client_mock

    return sendgrid_mock, post_mock


def _call_email_endpoint(context, device_id=None):
    """Build the request to the email endpoint and issue a call."""
    if device_id is None:
        login = context.device_login
        request_device_id = login["uuid"]
        request_headers = dict(Authorization=f"Bearer {login['accessToken']}")
    else:
        request_device_id = device_id
        request_headers = dict()
    request_data = dict(
        title="this is a test", sender="test@test.com", body="body message"
    )
    context.response = context.client.put(
        f"/v1/device/{request_device_id}/message",
        data=json.dumps(request_data),
        content_type="application/json",
        headers=request_headers,
    )


@then("an email should be sent to the account that owns the device")
def validate_response(context):
    """Validate that the SendGrid API was called as expected."""
    sendgrid_patch = context.sendgrid_patch
    sendgrid_patch.assert_called_with(api_key="test_sendgrid_key")
    post_mock = context.post_mock
    post_mock.assert_called_with(request_body=context.message_patch().get())
