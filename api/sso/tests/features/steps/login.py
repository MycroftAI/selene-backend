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

from binascii import b2a_base64
from http import HTTPStatus
import json
from unittest.mock import patch

from behave import given, then, when
from hamcrest import assert_that, equal_to

from selene.testing.api import validate_token_cookies

VALIDATE_FEDERATED = 'sso_api.endpoints.validate_federated.'


@given('user enters email address "{email}" and password "{password}"')
def save_credentials(context, email, password):
    context.email = email
    context.password = password


@given('user "{email}" authenticates through facebook')
def save_email(context, email):
    context.email = email


@when('single sign on validates the account')
def call_validate_federated_endpoint(context):
    func_to_patch = VALIDATE_FEDERATED + 'get_facebook_account_email'
    with patch(func_to_patch, return_value=context.email):
        context.response = context.client.post(
            '/api/validate-federated',
            data=json.dumps(dict(platform='Facebook', token='facebook_token')),
            content_type='application/json'
        )


@when('user attempts to login')
def call_internal_login_endpoint(context):
    credentials = '{}:||:{}'.format(context.email, context.password).encode()
    credentials = b2a_base64(credentials, newline=False).decode()
    context.response = context.client.get(
        '/api/internal-login',
        headers=dict(Authorization='Basic ' + credentials))


@then('login request succeeds')
def check_for_login_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )


@then('response contains authentication tokens')
def check_token_cookies(context):
    validate_token_cookies(context)


@then('login fails with "{error_message}" error')
def check_for_login_fail(context, error_message):
    assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    response_json = context.response.get_json()
    assert_that(response_json['error'], equal_to(error_message))
