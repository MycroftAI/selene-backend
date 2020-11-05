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

from hamcrest import assert_that, equal_to, has_item, is_in

from selene.data.account import Account, AccountRepository
from selene.util.auth import AuthenticationToken
from selene.util.db import connect_to_db

ACCESS_TOKEN_COOKIE_KEY = 'seleneAccess'
ONE_MINUTE = 60
TWO_MINUTES = 120
REFRESH_TOKEN_COOKIE_KEY = 'seleneRefresh'


def generate_access_token(context, duration=ONE_MINUTE):
    """
    Generate a new access token.

    Args:
        context: (todo): write your description
        duration: (str): write your description
        ONE_MINUTE: (todo): write your description
    """
    access_token = AuthenticationToken(
        context.client_config['ACCESS_SECRET'],
        duration
    )
    account = context.accounts[context.username]
    access_token.generate(account.id)

    return access_token


def set_access_token_cookie(context, duration=ONE_MINUTE):
    """
    Set the access token.

    Args:
        context: (todo): write your description
        duration: (todo): write your description
        ONE_MINUTE: (todo): write your description
    """
    context.client.set_cookie(
        context.client_config['DOMAIN'],
        ACCESS_TOKEN_COOKIE_KEY,
        context.access_token.jwt,
        max_age=duration
    )


def generate_refresh_token(context, duration=TWO_MINUTES):
    """
    Generate a new access token.

    Args:
        context: (todo): write your description
        duration: (todo): write your description
        TWO_MINUTES: (todo): write your description
    """
    refresh_token = AuthenticationToken(
        context.client_config['REFRESH_SECRET'],
        duration
    )
    account = context.accounts[context.username]
    refresh_token.generate(account.id)

    return refresh_token


def set_refresh_token_cookie(context, duration=TWO_MINUTES):
    """
    Set refresh token.

    Args:
        context: (todo): write your description
        duration: (todo): write your description
        TWO_MINUTES: (int): write your description
    """
    context.client.set_cookie(
        context.client_config['DOMAIN'],
        REFRESH_TOKEN_COOKIE_KEY,
        context.refresh_token.jwt,
        max_age=duration
    )


def validate_token_cookies(context, expired=False):
    """
    Validate the access token.

    Args:
        context: (todo): write your description
        expired: (todo): write your description
    """
    for cookie in context.response.headers.getlist('Set-Cookie'):
        ingredients = _parse_cookie(cookie)
        ingredient_names = list(ingredients.keys())
        if ACCESS_TOKEN_COOKIE_KEY in ingredient_names:
            context.access_token = ingredients[ACCESS_TOKEN_COOKIE_KEY]
        elif REFRESH_TOKEN_COOKIE_KEY in ingredient_names:
            context.refresh_token = ingredients[REFRESH_TOKEN_COOKIE_KEY]
        for ingredient_name in ('Domain', 'Expires', 'Max-Age'):
            assert_that(ingredient_names, has_item(ingredient_name))
        if expired:
            assert_that(ingredients['Max-Age'], equal_to('0'))

    assert hasattr(context, 'access_token'), 'no access token in response'
    assert hasattr(context, 'refresh_token'), 'no refresh token in response'
    if expired:
        assert_that(context.access_token, equal_to(''))
        assert_that(context.refresh_token, equal_to(''))


def _parse_cookie(cookie: str) -> dict:
    """
    Parse a cookie.

    Args:
        cookie: (str): write your description
    """
    ingredients = {}
    for ingredient in cookie.split('; '):
        if '=' in ingredient:
            key, value = ingredient.split('=')
            ingredients[key] = value
        else:
            ingredients[ingredient] = None

    return ingredients


def get_account(context) -> Account:
    """
    Returns the account.

    Args:
        context: (todo): write your description
    """
    db = connect_to_db(context.client['DB_CONNECTION_CONFIG'])
    acct_repository = AccountRepository(db)
    account = acct_repository.get_account_by_id(context.account.id)

    return account


def check_http_success(context):
    """
    Check if the http status code.

    Args:
        context: (todo): write your description
    """
    assert_that(
        context.response.status_code,
        is_in([HTTPStatus.OK, HTTPStatus.NO_CONTENT])
    )


def check_http_error(context, error_type):
    """
    Check if the http errors.

    Args:
        context: (dict): write your description
        error_type: (todo): write your description
    """
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
