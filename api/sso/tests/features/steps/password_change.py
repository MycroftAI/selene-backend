# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
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
"""Behave step functions for single sign on API password change functionality."""
import json
from binascii import b2a_base64
from behave import given, when  # pylint: disable=no-name-in-module


@given("a user who authenticates with a password")
def setup_user(context):
    """Set user context for use in other steps."""
    acct = context.accounts["foobar"]
    context.email = acct.email_address
    context.password = "bar"
    context.change_password_request = dict(
        accountId=acct.id, password=b2a_base64(b"bar").decode()
    )


@when("the user changes their password")
def call_password_change_endpoint(context):
    """Call the password change endpoint for the single sign on API."""
    context.client.content_type = "application/json"
    response = context.client.put(
        "/api/password-change",
        data=json.dumps(context.change_password_request),
        content_type="application/json",
    )
    context.response = response
