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
"""Step functions for the audio transcription endpoints of the Device API."""
import json
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from behave import when, then  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to

from selene.data.metric import TranscriptionMetricRepository


@when('Utterance "{utterance}" is transcribed using Google\'s STT API')
def call_google_stt_endpoint(context, utterance):
    """Call the endpoint with an audio file known to contain a certain phrase."""
    context.engine = "Google"
    context.utterance = utterance
    audio_data = _build_audio_data()
    request_headers = _build_request_header(context)
    context.response = context.client.post(
        "/v1/stt?lang=en-US&limit=1", data=audio_data, headers=request_headers
    )


@when('Utterance "{utterance}" is transcribed using Mycroft\'s transcription service')
def call_audio_transcription_endpoint(context, utterance):
    """Call the endpoint with an audio file known to contain a certain phrase."""
    context.engine = "Google Cloud"
    context.utterance = utterance
    audio_data = _build_audio_data()
    request_headers = _build_request_header(context)
    context.response = context.client.post(
        "/v1/transcribe?language=en-US", data=audio_data, headers=request_headers
    )


def _build_audio_data() -> BytesIO:
    """Converts a .flac file into a byte stream to pass to the endpoint."""
    resources_dir = Path(__file__).parent.joinpath("resources")
    with open(resources_dir.joinpath("test_stt.flac"), "rb") as flac_file:
        audio_data = BytesIO(flac_file.read())

    return audio_data


def _build_request_header(context):
    """Builds the authentication header for calling the Public API endpoint."""
    access_token = context.device_login["accessToken"]
    headers = dict(Authorization=f"Bearer {access_token}")

    return headers


@then("Google's transcription will be correct")
def validate_google_response(context):
    """Check that the right phrase was returned by Google STT."""
    response_data = json.loads(context.response.data)
    expected_response = [context.utterance]
    assert_that(response_data, equal_to(expected_response))


@then("the transcription will be returned to the device")
def validate_transcription_response(context):
    """Validates that the transcription endpoint returns the correct result."""
    assert_that(context.response.json["transcription"], equal_to(context.utterance))


@then("the transcription metrics for will be added to the database")
def validate_transcription_metrics(context):
    """Checks values are present in the metrics.stt_transcription table."""
    transcription_metric_repo = TranscriptionMetricRepository(context.db)
    metrics = transcription_metric_repo.get_by_account(context.account.id)
    assert_that(len(metrics), equal_to(1))
    metric = metrics[0]
    assert_that(metric.engine, equal_to(context.engine))
    assert_that(metric.account_id, equal_to(context.account.id))
    expected_audio_duration = metric.audio_duration.quantize((Decimal("0.001")))
    assert_that(expected_audio_duration, equal_to(Decimal("2.100")))
