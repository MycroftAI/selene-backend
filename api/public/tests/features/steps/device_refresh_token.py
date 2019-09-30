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
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key, is_not


@when('the session token is refreshed')
def refresh_token(context):
    login = json.loads(context.activate_device_response.data)
    refresh = login['refreshToken']
    context.refresh_token_response = context.client.get(
        '/v1/auth/token',
        headers={'Authorization': 'Bearer {token}'.format(token=refresh)}
    )


@then('a valid new session entity should be returned')
def validate_refresh_token(context):
    response = context.refresh_token_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))

    new_login = json.loads(response.data)
    assert_that(new_login, has_key(equal_to('uuid')))
    assert_that(new_login, has_key(equal_to('accessToken')))
    assert_that(new_login, has_key(equal_to('refreshToken')))
    assert_that(new_login, has_key(equal_to('expiration')))

    old_login = json.loads(context.activate_device_response.data)
    assert_that(new_login['uuid']), equal_to(old_login['uuid'])
    assert_that(new_login['accessToken'], is_not(equal_to(old_login['accessToken'])))
    assert_that(new_login['refreshToken'], is_not(equal_to(old_login['refreshToken'])))


@when('try to refresh an invalid refresh token')
def refresh_invalid_token(context):
    context.refresh_invalid_token_response = context.client.get(
        '/v1/auth/token',
        headers={'Authorization': 'Bearer {token}'.format(token='123')}
    )


@then('401 status code should be returned')
def validate_refresh_invalid_token(context):
    response = context.refresh_invalid_token_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
