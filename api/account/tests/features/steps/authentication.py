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

from behave import given, then
from hamcrest import assert_that, equal_to, is_not

from selene.testing.api import (
    generate_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
    validate_token_cookies
)
from selene.util.auth import AuthenticationToken

EXPIRE_IMMEDIATELY = 0


@given('an account with a valid access token')
def use_account_with_valid_access_token(context):
    context.username = 'foo'
    context.access_token = generate_access_token(context)
    set_access_token_cookie(context)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)


@given('an account with an expired access token')
def generate_expired_access_token(context):
    context.username = 'foo'
    context.access_token = generate_access_token(
        context,
        duration=EXPIRE_IMMEDIATELY
    )
    set_access_token_cookie(context, duration=EXPIRE_IMMEDIATELY)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)
    context.old_refresh_token = context.refresh_token.jwt


@given('an account with a refresh token but no access token')
def generate_refresh_token_only(context):
    context.username = 'foo'
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)
    context.old_refresh_token = context.refresh_token.jwt


@given('an account with expired access and refresh tokens')
def expire_both_tokens(context):
    context.username = 'foo'
    context.access_token = generate_access_token(
        context,
        duration=EXPIRE_IMMEDIATELY
    )
    set_access_token_cookie(context, duration=EXPIRE_IMMEDIATELY)
    context.refresh_token = generate_refresh_token(
        context,
        duration=EXPIRE_IMMEDIATELY
    )
    set_refresh_token_cookie(context, duration=EXPIRE_IMMEDIATELY)


@then('the authentication tokens will remain unchanged')
def check_for_no_new_cookie(context):
    cookies = context.response.headers.getlist('Set-Cookie')
    assert_that(cookies, equal_to([]))


@then('the authentication tokens will be refreshed')
def check_for_new_cookies(context):
    validate_token_cookies(context)
    assert_that(
        context.refresh_token,
        is_not(equal_to(context.old_refresh_token))
    )
    refresh_token = AuthenticationToken(
        context.client_config['REFRESH_SECRET'],
        0
    )
    refresh_token.jwt = context.refresh_token
    refresh_token.validate()
    assert_that(refresh_token.is_valid, equal_to(True))
    assert_that(refresh_token.is_expired, equal_to(False))
    assert_that(
        refresh_token.account_id,
        equal_to(context.accounts['foo'].id))
