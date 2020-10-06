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
from datetime import datetime
from pathlib import Path

from behave import then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to, is_in

from selene.data.tagging import UPLOADED_STATUS, WakeWordFile, WakeWordFileRepository
from selene.data.wake_word import WakeWord
from selene.testing.tagging import add_wake_word_file

AUDIO_FILE_NAME = "c46e74fa09732bb8d5e3aa4d8f46072bae9b732d.wav"
DUPLICATE_FILE_NAME = "c46e74fa09732bb8d5e3aa4d8f46072bae9b732d.0.wav"


@when("the device uploads a wake word file")
def upload_known_wake_word_file(context):
    """Upload a wake word sample file using the public API"""
    _build_expected_wake_word_file(context, wake_word="hey selene")
    wake_word_request = dict(
        wake_word="hey selene",
        engine="precise",
        timestamp="12345",
        model="selene_test_model",
    )
    _call_upload_endpoint(context, wake_word_request)


@when("the hash value of the file being uploaded matches a previous upload")
def add_collision_file(context):
    """Add a tagging.file row representing a file that resolves to same hash."""
    add_wake_word_file(context, AUDIO_FILE_NAME)
    context.duplicate_hash = True


@when("the device uploads a wake word file for an unknown wake word")
def upload_unknown_wake_word_file(context):
    """Upload a wake word sample file using the public API"""
    context.wake_words["computer"] = WakeWord(name="computer", engine="test")
    _build_expected_wake_word_file(context, "computer")
    wake_word_request = dict(
        wake_word="computer",
        engine="test",
        timestamp="12345",
        model="selene_test_model",
    )
    _call_upload_endpoint(context, wake_word_request)


def _build_expected_wake_word_file(context, wake_word):
    """Helper function to build a WakeWordFile object and store it in context."""
    wake_word_file = WakeWordFile(
        wake_word=context.wake_words[wake_word],
        name=AUDIO_FILE_NAME,
        origin="mycroft",
        submission_date=datetime.utcnow().date(),
        location=None,
        status=UPLOADED_STATUS,
        account_id=context.account.id,
    )
    context.expected_wake_word_file = wake_word_file


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
        context.expected_wake_word_file.wake_word.name.replace(" ", "-")
    )
    if context.duplicate_hash:
        expected_file_name = DUPLICATE_FILE_NAME
    else:
        expected_file_name = AUDIO_FILE_NAME
    file_path = file_dir.joinpath(expected_file_name)
    assert file_path.exists()


@then("a reference to the sample is stored in the database")
def check_wake_word_file_table(context):
    """The data representing the audio file is stored correctly on the database."""
    file_repository = WakeWordFileRepository(context.db)
    context.wake_word_files = file_repository.get_by_wake_word(
        context.expected_wake_word_file.wake_word
    )
    if context.duplicate_hash:
        expected_file_names = [AUDIO_FILE_NAME, DUPLICATE_FILE_NAME]
        file_count = 2
    else:
        expected_file_names = [AUDIO_FILE_NAME]
        file_count = 1
    assert_that(len(context.wake_word_files), equal_to(file_count))
    for wake_word_file in context.wake_word_files:
        assert_that(wake_word_file.name, is_in(expected_file_names))
        assert_that(
            wake_word_file.location.directory,
            context.wake_word_dir.joinpath(
                context.expected_wake_word_file.wake_word.name.replace(" ", "-")
            ),
        )
        assert_that(wake_word_file.location.server, equal_to("127.0.0.1"))
