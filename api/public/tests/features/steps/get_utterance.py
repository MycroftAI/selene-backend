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
"""Step functions for the Google STT endpoint of the Device API."""
import json
import os
from io import BytesIO

from behave import when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to


@when('A flac audio with the utterance "what time is it" is passed')
def call_google_stt_endpoint(context):
    """Call the endpoint with an audio file known to contain a certain phrase."""
    access_token = context.device_login["accessToken"]
    headers = dict(Authorization=f"Bearer {access_token}")
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    with open(os.path.join(resources_dir, "test_stt.flac"), "rb") as flac:
        audio = BytesIO(flac.read())
        context.response = context.client.post(
            "/v1/stt?lang=en-US&limit=1", data=audio, headers=headers
        )


@then('return the utterance "what time is it"')
def validate_response(context):
    """Check that the right phrase was returned by Google STT."""
    response_data = json.loads(context.response.data)
    expected_response = ["what time is it"]
    assert_that(response_data, equal_to(expected_response))
