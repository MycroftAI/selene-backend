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

from behave import given, then
from hamcrest import assert_that, equal_to, is_in

from selene.testing.api import (
    generate_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie
)


@given('the account is authenticated')
def use_account_with_valid_access_token(context):
    context.access_token = generate_access_token(context)
    set_access_token_cookie(context)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)


@then('the request will be successful')
def check_request_success(context):
    assert_that(
        context.response.status_code,
        is_in([HTTPStatus.OK, HTTPStatus.NO_CONTENT])
    )


@then('the request will fail with {error_type} error')
def check_for_bad_request(context, error_type):
    if error_type == 'a bad request':
        assert_that(
            context.response.status_code,
            equal_to(HTTPStatus.BAD_REQUEST)
        )
    elif error_type == 'an unauthorized':
        assert_that(
            context.response.status_code,
            equal_to(HTTPStatus.UNAUTHORIZED)
        )
    else:
        raise ValueError('unsupported error_type')
