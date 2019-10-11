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

from http import HTTPStatus
from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item, is_not

from selene.api.testing import (
    generate_access_token,
    generate_refresh_token,
    get_account,
    validate_token_cookies
)


@given('user "{email}" is authenticated')
def save_email(context, email):
    context.email = email


@when('user attempts to logout')
def call_logout_endpoint(context):
    generate_access_token(context)
    generate_refresh_token(context)
    context.response = context.client.get('/api/logout')


@then('request is successful')
def check_for_logout_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.NO_CONTENT))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )


@then('response contains expired token cookies')
def check_response_cookies(context):
    validate_token_cookies(context, expired=True)


@then('logout fails with "{error_message}" error')
def check_for_login_fail(context, error_message):
    assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    assert_that(context.response.get_json(), equal_to(error_message))
