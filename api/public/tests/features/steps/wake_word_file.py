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
"""Step functions for the wake word sample upload feature."""
import os
from pathlib import Path

from behave import then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to

from selene.data.tagging import WakeWordFileRepository
from selene.data.wake_word import WakeWord


@when("the device uploads a wake word file")
def upload_known_wake_word_file(context):
    """Upload a wake word sample file using the public API"""
    context.scenario_wake_word = "hey selene"
    wake_word_request = dict(
        wake_word="hey selene",
        engine="precise",
        timestamp="12345",
        model="selene_test_model",
    )
    _call_upload_endpoint(context, wake_word_request)


@when("the device uploads a wake word file for an unknown wake word")
def upload_unknown_wake_word_file(context):
    """Upload a wake word sample file using the public API"""
    context.wake_words["computer"] = WakeWord(name="computer", engine="test")
    context.scenario_wake_word = "computer"
    wake_word_request = dict(
        wake_word="computer",
        engine="test",
        timestamp="12345",
        model="selene_test_model",
    )
    _call_upload_endpoint(context, wake_word_request)


def _call_upload_endpoint(context, request):
    """Upload a wake word sample file using the public API"""
    resources_dir = Path(os.path.dirname(__file__)).joinpath("resources")
    audio_file_path = str(resources_dir.joinpath("wake_word_test.wav"))
    access_token = context.device_login["accessToken"]
    with open(audio_file_path, "rb") as audio_file:
        request.update(audio_file=(audio_file, "wake_word.wav"))
        response = context.client.post(
            f"/v1/device/{context.device_id}/wake-word-file",
            headers=dict(Authorization="Bearer {token}".format(token=access_token)),
            data=request,
            content_type="multipart/form-data",
        )
    context.response = response


@then("the audio file is saved to a temporary directory")
def check_file_save(context):
    """The audio file containing the wake word sample is saved to the right location."""

    file_dir = context.wake_word_dir.joinpath(
        context.scenario_wake_word.replace(" ", "-")
    )
    file_name = context.account.id + ".12345.wav"
    file_path = file_dir.joinpath(file_name)
    assert file_path.exists()


@then("a reference to the sample is stored in the database")
def check_wake_word_file_table(context):
    """The data representing the audio file is stored correctly on the database."""
    file_repository = WakeWordFileRepository(context.db)
    wake_word = context.wake_words[context.scenario_wake_word]
    wake_word_files = file_repository.get_by_wake_word(wake_word)
    assert_that(len(wake_word_files), equal_to(1))
    wake_word_file = wake_word_files[0]
    assert_that(wake_word_file.name, equal_to(context.account.id + ".12345.wav"))
    assert_that(
        wake_word_file.location.directory,
        context.wake_word_dir.joinpath(context.scenario_wake_word.replace(" ", "-")),
    )
    assert_that(wake_word_file.location.server, equal_to("127.0.0.1"))
