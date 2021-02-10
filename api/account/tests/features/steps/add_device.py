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
"""Python code to support the add device feature."""
import json
from unittest.mock import MagicMock, patch

from behave import given, when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to, none, not_none

from selene.data.device import DeviceRepository
from selene.util.cache import (
    DEVICE_PAIRING_CODE_KEY,
    DEVICE_PAIRING_TOKEN_KEY,
    SeleneCache,
)
from selene.util.db import connect_to_db


@given("a device pairing code")
def set_device_pairing_code(context):
    """Add dummy data to the Redis cache for the test."""
    pairing_data = dict(
        code="ABC123",
        packaging_type="pantacor",
        state="this is a state",
        token="this is a token",
        expiration=84600,
    )
    cache = SeleneCache()
    cache.set_with_expiration(
        "pairing.code:ABC123", json.dumps(pairing_data), expiration=86400
    )
    context.pairing_data = pairing_data
    context.pairing_code = "ABC123"


@when("an API request is sent to add a device")
def add_device(context):
    """Call the endpoint to add a device based on user input."""
    device = dict(
        city="Kansas City",
        country="United States",
        name="Selene Test Device",
        pairingCode=context.pairing_code,
        placement="Mycroft Offices",
        region="Missouri",
        timezone="America/Chicago",
        wakeWord="hey selene",
        voice="Selene Test Voice",
    )
    with patch("requests.request") as request_patch:
        get_channel_content = dict(
            items=[dict(id="test_channel_id", name="test_channel_name")]
        )
        get_channel_response = MagicMock(spec=["ok", "content"])
        get_channel_response.ok = True
        get_channel_response.content = json.dumps(get_channel_content).encode()

        get_device_content = dict(
            items=[
                dict(
                    id="test_device_id",
                    channel_id="test_channel_id",
                    update_policy="auto",
                    labels=["device-meta/interfaces.wlan0.ipv4.0=192.168.1.2"],
                )
            ]
        )
        get_device_response = MagicMock(spec=["ok", "content"])
        get_device_response.ok = True
        get_device_response.content = json.dumps(get_device_content).encode()

        request_patch.side_effect = [get_channel_response, get_device_response]
        response = context.client.post(
            "/api/devices", data=json.dumps(device), content_type="application_json"
        )
    context.response = response


@then("the pairing code is removed from cache")
def validate_pairing_code_removal(context):
    """Ensure that the endpoint removed the pairing code entry from the cache."""
    cache = SeleneCache()
    pairing_data = cache.get(
        DEVICE_PAIRING_CODE_KEY.format(pairing_code=context.pairing_code)
    )
    assert_that(pairing_data, none())


@then("the device is added to the database")
def validate_response(context):
    """Ensure that the database was updated as expected."""
    device_id = context.response.data.decode()
    account = context.accounts["foo"]
    db = connect_to_db(context.client_config["DB_CONNECTION_CONFIG"])
    device_repository = DeviceRepository(db)
    device = device_repository.get_device_by_id(device_id)

    assert_that(device, not_none())
    assert_that(device.name, equal_to("Selene Test Device"))
    assert_that(device.placement, equal_to("Mycroft Offices"))
    assert_that(device.account_id, equal_to(account.id))
    assert_that(device.pantacor_config.pantacor_id, equal_to("test_device_id"))
    assert_that(device.pantacor_config.ip_address, equal_to("192.168.1.2"))
    assert_that(device.pantacor_config.auto_update, equal_to(True))
    assert_that(device.pantacor_config.ssh_public_key, none())
    assert_that(device.pantacor_config.release_channel, equal_to("test_channel_name"))


@then("the pairing token is added to cache")
def validate_pairing_token(context):
    """Validate the pairing token data was added to the cache as expected."""
    device_id = context.response.data.decode()
    cache = SeleneCache()
    pairing_data = cache.get(
        DEVICE_PAIRING_TOKEN_KEY.format(pairing_token="this is a token")
    )
    pairing_data = json.loads(pairing_data)

    assert_that(pairing_data["uuid"], equal_to(device_id))
    assert_that(pairing_data["state"], equal_to(context.pairing_data["state"]))
    assert_that(pairing_data["token"], equal_to(context.pairing_data["token"]))
