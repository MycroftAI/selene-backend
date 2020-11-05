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
import uuid
from http import HTTPStatus
from unittest.mock import patch, MagicMock

from behave import when, then
from hamcrest import assert_that, equal_to

email_request = dict(
    title='this is a test',
    sender='test@test.com',
    body='body message'
)


@when('an email message is sent to the email endpoint')
@patch('smtplib.SMTP')
def send_email(context, email_client):
    """
    Sends email.

    Args:
        context: (dict): write your description
        email_client: (str): write your description
    """
    context.client_config['EMAIL_CLIENT'] = email_client
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    context.email_response = context.client.put(
        '/v1/device/{uuid}/message'.format(uuid=device_id),
        data=json.dumps(email_request),
        content_type='application_json',
        headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    )


@then('an email should be sent to the user\'s account that owns the device')
def validate_response(context):
    """
    Validate response.

    Args:
        context: (todo): write your description
    """
    response = context.email_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    email_client: MagicMock = context.client_config['EMAIL_CLIENT']
    email_client.send_message.assert_called()


@when('the email endpoint is called by a not allowed device')
@patch('smtplib.SMTP')
def send_email_invalid_device(context, email_client):
    """
    Send an email address.

    Args:
        context: (todo): write your description
        email_client: (todo): write your description
    """
    context.client_config['EMAIL_CLIENT'] = email_client
    context.email_invalid_response = context.client.put(
        '/v1/device/{uuid}/email'.format(uuid=str(uuid.uuid4())),
        data=json.dumps(email_request),
        content_type='application_json'
    )


@then('401 status code should be returned by the email endpoint')
def validate_response_invalid_device(context):
    """
    Validate the response payload.

    Args:
        context: (todo): write your description
    """
    response = context.email_invalid_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    email_client: MagicMock = context.client_config['EMAIL_CLIENT']
    email_client.send_message.assert_not_called()
