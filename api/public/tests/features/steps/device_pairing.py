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
"""Python code to support the device pairing feature."""
import json
import uuid

# from unittest.mock import patch

from behave import given, then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to, has_key

from selene.util.cache import DEVICE_PAIRING_CODE_KEY, DEVICE_PAIRING_TOKEN_KEY

ONE_MINUTE = 60
ONE_DAY = 86400


@given("the user completes the pairing process on the web application")
def add_device(context):
    """Imitate the logic in the account API to pair a device"""
    context.pairing_token = "pairing_token"
    context.pairing_state = "pairing_state"
    pairing_data = dict(
        code="ABC123",
        uuid=context.device_id,
        state=context.pairing_state,
        token=context.pairing_token,
        expiration=ONE_DAY,
    )
    context.cache.set_with_expiration(
        key=DEVICE_PAIRING_TOKEN_KEY.format(pairing_token=context.pairing_token),
        value=json.dumps(pairing_data),
        expiration=ONE_MINUTE,
    )


@when("a device requests a pairing code")
def get_device_pairing_code(context):
    """Call the endpoint that generates the pairing data."""
    context.state = str(uuid.uuid4())
    response = context.client.get(
        "/v1/device/code?state={state}&packaging=pantacor".format(state=context.state)
    )
    context.response = response


@when("the device requests to be activated")
def activate_device(context):
    """Call the endpoint that completes the device registration process."""
    activation_request = dict(
        token=context.pairing_token,
        state=context.pairing_state,
        platform="picroft",
        coreVersion="18.8.0",
        enclosureVersion="1.4.0",
    )
    response = context.client.post(
        "/v1/device/activate",
        data=json.dumps(activation_request),
        content_type="application/json",
    )
    context.response = response


@then("the pairing data is stored in Redis")
def check_cached_pairing_data(context):
    """Confirm that the pairing data stored in Redis is as expected."""
    pairing_code_key = DEVICE_PAIRING_CODE_KEY.format(
        pairing_code=context.response.json["code"]
    )
    pairing_data = context.cache.get(pairing_code_key)
    pairing_data = json.loads(pairing_data)
    context.cache.delete(pairing_code_key)
    assert_that(pairing_data, has_key("token"))
    assert_that(pairing_data["code"], equal_to(context.response.json["code"]))
    assert_that(pairing_data["expiration"], equal_to(ONE_DAY))
    assert_that(pairing_data["state"], equal_to(context.state))
    assert_that(pairing_data["packaging_type"], equal_to("pantacor"))


@then("the pairing data is sent to the device")
def validate_pairing_code_response(context):
    """Check that the endpoint returns the expected pairing data to the device"""
    response = context.response
    assert_that(response.json, has_key("code"))
    assert_that(response.json, has_key("token"))
    assert_that(response.json["expiration"], equal_to(ONE_DAY))
    assert_that(response.json["state"], equal_to(context.state))


@then("the activation data is sent to the device")
def validate_activation_response(context):
    """Check that the endpoint returns the expected activation data to the device."""
    response = context.response
    assert_that(response.json["uuid"], equal_to(context.device_id))
    assert_that(response.json, has_key("accessToken"))
    assert_that(response.json, has_key("refreshToken"))
    assert_that(response.json["expiration"], equal_to(ONE_DAY))
