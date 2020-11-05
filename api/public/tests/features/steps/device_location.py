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

from behave import when, then, given
from hamcrest import assert_that, equal_to, has_key, not_none, is_not

from selene.api.etag import ETagManager, device_location_etag_key


@when('a api call to get the location is done')
def get_device_location(context):
    """
    Get the location of the context.

    Args:
        context: (todo): write your description
    """
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_location_response = context.client.get(
        '/v1/device/{uuid}/location'.format(uuid=device_id),
        headers=headers
    )


@then('the location should be retrieved')
def validate_location(context):
    """
    Check if a location.

    Args:
        context: (todo): write your description
    """
    response = context.get_location_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    location = json.loads(response.data)
    assert_that(location, has_key('coordinate'))
    assert_that(location, has_key('timezone'))
    assert_that(location, has_key('city'))

    coordinate = location['coordinate']
    assert_that(coordinate, has_key('latitude'))
    assert_that(coordinate, has_key('longitude'))

    timezone = location['timezone']
    assert_that(timezone, has_key('name'))
    assert_that(timezone, has_key('code'))
    assert_that(timezone, has_key('offset'))
    assert_that(timezone, has_key('dstOffset'))

    city = location['city']
    assert_that(city, has_key('name'))
    assert_that(city, has_key('state'))

    state = city['state']
    assert_that(state, has_key('name'))
    assert_that(state, has_key('country'))
    assert_that(state, has_key('code'))

    country = state['country']
    assert_that(country, has_key('name'))
    assert_that(country, has_key('code'))


@given('an expired etag from a location entity')
def expire_location_etag(context):
    """
    Expire the location of the iag.

    Args:
        context: (todo): write your description
    """
    etag_manager: ETagManager = context.etag_manager
    device_id = context.device_login['uuid']
    context.expired_location_etag = etag_manager.get(device_location_etag_key(device_id))
    etag_manager.expire_device_location_etag_by_device_id(device_id)


@when('try to get the location using the expired etag')
def get_using_expired_etag(context):
    """
    Get an access token.

    Args:
        context: (todo): write your description
    """
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': context.expired_location_etag
    }
    context.get_location_response = context.client.get(
        '/v1/device/{uuid}/location'.format(uuid=device_id),
        headers=headers
    )


@then('an etag associated with the location should be created')
def validate_etag(context):
    """
    Validate the etag.

    Args:
        context: (todo): write your description
    """
    response = context.get_location_response
    new_location_etag = response.headers.get('ETag')
    assert_that(new_location_etag, not_none())
    assert_that(new_location_etag, is_not(context.expired_location_etag))


@given('a valid etag from a location entity')
def valid_etag(context):
    """
    Check if the etag is valid.

    Args:
        context: (todo): write your description
    """
    etag_manager = context.etag_manager
    device_id = context.device_login['uuid']
    context.valid_location_etag = etag_manager.get(device_location_etag_key(device_id))


@when('try to get the location using a valid etag')
def get_using_valid_etag(context):
    """
    Get an etag.

    Args:
        context: (todo): write your description
    """
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': context.valid_location_etag
    }
    context.get_location_response = context.client.get(
        '/v1/device/{uuid}/location'.format(uuid=device_id),
        headers=headers
    )


@then('the location endpoint should return 304')
def validate_response_valid_etag(context):
    """
    Validate response response.

    Args:
        context: (todo): write your description
    """
    response = context.get_location_response
    assert_that(response.status_code, equal_to(HTTPStatus.NOT_MODIFIED))
