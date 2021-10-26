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

from behave import when, then
from hamcrest import assert_that


@when("a question is sent to the Wolfram Alpha full results endpoint")
def send_question(context):
    login = context.device_login
    access_token = login["accessToken"]
    context.wolfram_response = context.client.get(
        "/v1/wolframAlphaFull?input=what+is+the+capital+of+Brazil",
        headers=dict(Authorization="Bearer {token}".format(token=access_token)),
    )


@when("a question is sent to the wolfram alpha spoken endpoint")
def send_question(context):
    login = context.device_login
    access_token = login["accessToken"]
    context.wolfram_response = context.client.get(
        "/v1/wolframAlphaSpoken?i=how+tall+was+abraham+lincoln&geolocation=51.50853%2C-0.12574&units=Metric",
        headers=dict(Authorization="Bearer {token}".format(token=access_token)),
    )


@then("the answer provided by Wolfram Alpha is returned")
def validate_response(context):
    response = context.wolfram_response
    assert_that(response.status_code, HTTPStatus.OK)
