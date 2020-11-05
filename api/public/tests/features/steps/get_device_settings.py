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

from behave import when, then, given
from hamcrest import assert_that, equal_to, has_key, is_not

from selene.api.etag import ETagManager, device_setting_etag_key


@when('try to fetch device\'s setting')
def get_device_settings(context):
    """
    Get settings.

    Args:
        context: (todo): write your description
    """
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    context.response_setting = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=device_id),
        headers=headers
    )


@then('a valid setting should be returned')
def validate_response_setting(context):
    """
    Validate the response setting.

    Args:
        context: (todo): write your description
    """
    response = context.response_setting
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    setting = json.loads(response.data)
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    assert_that(setting, has_key('uuid'))
    assert_that(setting, has_key('systemUnit'))
    assert_that(setting['systemUnit'], equal_to('imperial'))
    assert_that(setting, has_key('timeFormat'))
    assert_that(setting, has_key('dateFormat'))
    assert_that(setting, has_key('optIn'))
    assert_that(setting['optIn'], equal_to(True))
    assert_that(setting, has_key('ttsSettings'))
    tts = setting['ttsSettings']
    assert_that(tts, has_key('module'))


@when('the settings endpoint is a called to a not allowed device')
def get_device_settings(context):
    """
    Gets settings for the current user.

    Args:
        context: (todo): write your description
    """
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_invalid_setting_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(uuid.uuid4())),
        headers=headers
    )


@then('a 401 status code should be returned for the setting')
def validate_response(context):
    """
    Validate the response.

    Args:
        context: (todo): write your description
    """
    response = context.get_invalid_setting_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))


@given('a device\'s setting with a valid etag')
def get_device_setting_etag(context):
    """
    Gets the device setting for the device.

    Args:
        context: (todo): write your description
    """
    device_id = context.device_login['uuid']
    etag_manager: ETagManager = context.etag_manager
    context.device_etag = etag_manager.get(device_setting_etag_key(device_id))


@when('try to fetch the device\'s settings using a valid etag')
def get_device_settings_using_etag(context):
    """
    Gets iam settings.

    Args:
        context: (todo): write your description
    """
    etag = context.device_etag
    access_token = context.device_login['accessToken']
    device_id = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.get_setting_etag_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(device_id)),
        headers=headers
    )


@then('304 status code should be returned by the device\'s settings endpoint')
def validate_etag_response(context):
    """
    Validate the response.

    Args:
        context: (todo): write your description
    """
    response = context.get_setting_etag_response
    assert_that(response.status_code, equal_to(HTTPStatus.NOT_MODIFIED))


@given('a device\'s setting etag expired by the web ui at device level')
def expire_etag_device_level(context):
    """
    Expire the device level.

    Args:
        context: (todo): write your description
    """
    device_id = context.device_login['uuid']
    etag_manager: ETagManager = context.etag_manager
    context.device_etag = etag_manager.get(device_setting_etag_key(device_id))
    etag_manager.expire_device_setting_etag_by_device_id(device_id)


@given('a device\'s setting etag expired by the web ui at account level')
def expire_etag_account_level(context):
    """
    Expire the current login level.

    Args:
        context: (todo): write your description
    """
    account_id = context.account.id
    device_id = context.device_login['uuid']
    etag_manager: ETagManager = context.etag_manager
    context.device_etag = etag_manager.get(device_setting_etag_key(device_id))
    etag_manager.expire_device_setting_etag_by_account_id(account_id)


@when('try to fetch the device\'s settings using an expired etag')
def get_device_settings_using_etag(context):
    """
    Gets iam settings.

    Args:
        context: (todo): write your description
    """
    etag = context.device_etag
    access_token = context.device_login['accessToken']
    device_id = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.get_setting_invalid_etag_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(device_id)),
        headers=headers
    )


@then('200 status code should be returned by the device\'s setting endpoint and a new etag')
def validate_new_etag(context):
    """
    Validate a new etag.

    Args:
        context: (todo): write your description
    """
    etag = context.device_etag
    response = context.get_setting_invalid_etag_response
    etag_from_response = response.headers.get('ETag')
    assert_that(etag, is_not(etag_from_response))
