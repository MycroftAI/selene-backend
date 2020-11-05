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
"""Behave step functions for single sign on API logout functionality."""
from http import HTTPStatus
from behave import given, then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to

from selene.testing.api import (
    generate_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
    validate_token_cookies,
)


@given("an authenticated account")
def use_account_with_valid_access_token(context):
    """Setup test context with an authenticated account for future steps."""
    context.username = "foobar"
    context.access_token = generate_access_token(context)
    set_access_token_cookie(context)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)


@when("user attempts to logout")
def call_logout_endpoint(context):
    """Call the single sign on endpoint to logout a user."""
    generate_access_token(context)
    generate_refresh_token(context)
    context.response = context.client.get("/api/logout")


@then("response contains expired token cookies")
def check_response_cookies(context):
    """
    Checks if the token.

    Args:
        context: (dict): write your description
    """
    validate_token_cookies(context, expired=True)
