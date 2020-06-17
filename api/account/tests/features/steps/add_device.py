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

from behave import given, when, then
from hamcrest import assert_that, equal_to, none, not_none

from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db


@given("a device pairing code")
def set_device_pairing_code(context):
    pairing_data = dict(
        code="ABC123",
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
    device = dict(
        city="Kansas City",
        country="United States",
        name="Selene Test Device",
        pairingCode=context.pairing_code,
        placement="Mycroft Offices",
        region="Missouri",
        timezone="America/Chicago",
        wakeWord="Selene Test Wake Word",
        voice="Selene Test Voice",
    )
    response = context.client.post(
        "/api/devices", data=json.dumps(device), content_type="application_json"
    )
    context.response = response


@then("the pairing code is removed from cache")
def validate_pairing_code_removal(context):
    cache = SeleneCache()
    pairing_data = cache.get("pairing.code:ABC123")
    assert_that(pairing_data, none())


@then("the device is added to the database")
def validate_response(context):
    device_id = context.response.data.decode()
    account = context.accounts["foo"]
    db = connect_to_db(context.client_config["DB_CONNECTION_CONFIG"])
    device_repository = DeviceRepository(db)
    device = device_repository.get_device_by_id(device_id)

    assert_that(device, not_none())
    assert_that(device.name, equal_to("Selene Test Device"))
    assert_that(device.placement, equal_to("Mycroft Offices"))
    assert_that(device.account_id, equal_to(account.id))


@then("the pairing token is added to cache")
def validate_pairing_token(context):
    device_id = context.response.data.decode()
    cache = SeleneCache()
    pairing_data = cache.get("pairing.token:this is a token")
    pairing_data = json.loads(pairing_data)

    assert_that(pairing_data["uuid"], equal_to(device_id))
    assert_that(pairing_data["state"], equal_to(context.pairing_data["state"]))
    assert_that(pairing_data["token"], equal_to(context.pairing_data["token"]))
