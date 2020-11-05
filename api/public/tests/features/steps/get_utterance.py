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
import os
from http import HTTPStatus
from io import BytesIO

from behave import When, Then
from hamcrest import assert_that, equal_to, not_none


@When('A flac audio with the utterance "tell me a joke" is passed')
def call_google_stt_endpoint(context):
    """
    Call the google cloud provider.

    Args:
        context: (todo): write your description
    """
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    resources_dir = os.path.join(os.path.dirname(__file__), 'resources')
    with open(os.path.join(resources_dir, 'test_stt.flac'), 'rb') as flac:
        audio = BytesIO(flac.read())
        context.response = context.client.post(
            '/v1/stt?lang=en-US&limit=1',
            data=audio,
            headers=headers
        )


@Then('return the utterance "tell me a joke"')
def validate_response(context):
    """
    Validate the response.

    Args:
        context: (todo): write your description
    """
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(context.response.data)
    expected_response = ['tell me a joke']
    assert_that(response_data, equal_to(expected_response))

    resources_dir = os.path.join(os.path.dirname(__file__), 'resources')
    with open(os.path.join(resources_dir, 'test_stt.flac'), 'rb') as input_file:
        input_file_content = input_file.read()
    flac_file_path = _get_stt_result_file(context.account.id, '.flac')
    assert_that(flac_file_path, not_none())
    with open(flac_file_path, 'rb') as output_file:
        output_file_content = output_file.read()
    assert_that(input_file_content, equal_to(output_file_content))

    stt_file_path = _get_stt_result_file(context.account.id, '.stt')
    assert_that(stt_file_path, not_none())
    with open(stt_file_path, 'rb') as output_file:
        output_file_content = output_file.read()
    assert_that(b'tell me a joke', equal_to(output_file_content))


def _get_stt_result_file(account_id, file_suffix):
    """
    Returns the file_id for a file_stt file.

    Args:
        account_id: (str): write your description
        file_suffix: (str): write your description
    """
    file_path = None
    for stt_file_name in os.listdir('/opt/selene/data'):
        file_name_match = (
            stt_file_name.startswith(account_id)
            and stt_file_name.endswith(file_suffix)
        )
        if file_name_match:
            file_path = os.path.join('/opt/selene/data/', stt_file_name)

    return file_path
