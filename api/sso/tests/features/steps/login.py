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
"""Step functions for the login feature."""
from binascii import b2a_base64
from http import HTTPStatus
import json
from unittest.mock import patch

from behave import given, then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to

from selene.testing.api import validate_token_cookies

VALIDATE_FEDERATED = "sso_api.endpoints.validate_federated."


@given('user enters email address "{email}" and password "{password}"')
def save_credentials(context, email, password):
    """Save the email and password for use in later steps."""
    context.email = email
    context.password = password


@given('user "{email}" authenticates through {platform}')
def save_email(context, email, platform):
    """Save email and federated login platform for use in later steps"""
    context.email = email
    context.platform = platform


@when("single sign on validates the account")
def call_validate_federated_endpoint(context):
    """Call the single sign on endpoint to validate a token."""
    func_to_patch = VALIDATE_FEDERATED + "get_{}_account_email".format(
        context.platform.lower()
    )
    with patch(func_to_patch, return_value=context.email):
        context.response = context.client.post(
            "/api/validate-federated",
            data=json.dumps(dict(platform=context.platform, token="federated_token")),
            content_type="application/json",
        )


@when("user attempts to login")
def call_internal_login_endpoint(context):
    """Call the single sign on API endpoint to login with email & password."""
    credentials = "{}:||:{}".format(context.email, context.password).encode()
    credentials = b2a_base64(credentials, newline=False).decode()
    context.response = context.client.get(
        "/api/internal-login", headers=dict(Authorization="Basic " + credentials)
    )


@then("response contains authentication tokens")
def check_token_cookies(context):
    """Ensure proper JWTs for authentication are included in the cookies."""
    validate_token_cookies(context)
