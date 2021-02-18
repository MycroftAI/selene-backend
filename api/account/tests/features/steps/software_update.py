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
"""Step functions for applying a software update via the account API."""

import json
from unittest.mock import MagicMock, patch

from behave import given, then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to

from selene.testing.device import add_device, add_pantacor_config


@given("a device using Pantacor with manual updates enabled")
def add_pantacor_device(context):
    """Add a device with a Pantacor config and software update set to manual."""
    context.device_id = add_device(
        context.db, context.accounts["foo"].id, context.geography_id
    )
    add_pantacor_config(context.db, context.device_id)


@given("the device has pending deployment from Pantacor")
def add_pantacor_deployment_id(context):
    """Add a dummy deployment ID to the context for use later in tests."""
    context.deployment_id = "test_deployment_id"


@when("the user selects to apply the update")
def apply_software_update(context):
    """Make an API call to apply the software update.

    The Pantacor API code is patched because there is currently no way to call it
    reliably with a test device.
    """
    with patch("requests.request") as request_patch:
        apply_update_response = MagicMock(spec=["ok", "content"])
        apply_update_response.ok = True
        apply_update_response.content = '{"response":"ok"}'.encode()
        request_patch.side_effect = [apply_update_response]
        request_data = dict(deploymentId=context.deployment_id)
        response = context.client.patch(
            "/api/software-update",
            data=json.dumps(request_data),
            content_type="application/json",
        )
    context.response = response


@when("the user requests to view the device")
def get_device(context):
    """Make an API call to get device data, including a software update ID.

    The Pantacor API code is patched because there is currently no way to call it
    reliably with a test device.
    """
    with patch("requests.request") as request_patch:
        get_deployment_response = MagicMock(spec=["ok", "content"])
        get_deployment_response.ok = True
        get_deployment_content = dict(items=[dict(id="test_deployment_id",)])
        get_deployment_response.content = json.dumps(get_deployment_content).encode()
        request_patch.side_effect = [get_deployment_response]
        response = context.client.get(
            "/api/devices/" + context.device_id, content_type="application/json"
        )
    context.response = response


@then("the response contains the pending deployment ID")
def check_for_deployment_id(context):
    """Check the response of the device query to ensure the update ID is populated."""
    device_attributes = context.response.json
    assert_that(device_attributes["pantacorUpdateId"], equal_to("test_deployment_id"))
