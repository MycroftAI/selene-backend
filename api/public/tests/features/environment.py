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
"""Environmental controls for the public API behavioral tests"""
import os
from logging import getLogger
from pathlib import Path
from tempfile import mkdtemp

from behave import fixture, use_fixture

from public_api.api import public
from selene.api import generate_device_login
from selene.api.etag import ETagManager
from selene.testing.account import add_account, remove_account
from selene.testing.account_activity import remove_account_activity
from selene.testing.agreement import add_agreements, remove_agreements
from selene.testing.account_geography import add_account_geography
from selene.testing.account_preference import add_account_preference
from selene.testing.device import add_device
from selene.testing.device_skill import (
    add_device_skill,
    add_device_skill_settings,
    remove_device_skill,
)
from selene.testing.skill import (
    add_skill,
    build_checkbox_field,
    build_label_field,
    build_text_field,
    remove_skill,
)
from selene.testing.tagging import remove_wake_word_files
from selene.testing.text_to_speech import add_text_to_speech, remove_text_to_speech
from selene.testing.wake_word import add_wake_word, remove_wake_word
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db

_log = getLogger("public_api_behave_tests")


@fixture
def public_api_client(context):
    """Start the public API for use in the tests."""
    public.testing = True
    context.client_config = public.config
    context.client = public.test_client()
    yield context.client


def before_all(context):
    """Setup static test data before any tests run.

    This is data that does not change from test to test so it only needs to be setup
    and torn down once.
    """
    _log.info("setting up test suite...")
    use_fixture(public_api_client, context)
    context.cache = SeleneCache()
    context.db = connect_to_db(context.client_config["DB_CONNECTION_CONFIG"])
    add_agreements(context)
    context.wake_words = {"hey selene": add_wake_word(context.db)}
    data_dir = mkdtemp()
    context.wake_word_dir = Path(data_dir).joinpath("wake-word")
    os.environ["SELENE_DATA_DIR"] = data_dir


def after_all(context):
    """Clean up static test data after all tests have run.

    This is data that does not change from test to test so it only needs to be setup
    and torn down once.
    """
    _log.info("cleaning up test suite")
    try:
        for wake_word in context.wake_words.values():
            _remove_wake_word_files(context, wake_word)
            remove_wake_word(context.db, wake_word)
        remove_agreements(
            context.db,
            [context.privacy_policy, context.terms_of_use, context.open_dataset],
        )
        os.removedirs(context.wake_word_dir)
    except Exception:
        _log.exception("failure in test suite cleanup")
        raise


def _remove_wake_word_files(context, wake_word):
    """Delete the .wav files from the file system and their references on the database

    Assumes that there are no subdirectories in the provided temp directory.
    """
    file_dir = context.wake_word_dir.joinpath(wake_word.name.replace(" ", "-"))
    for file_name in os.listdir(file_dir):
        os.remove(file_dir.joinpath(file_name))
    os.rmdir(file_dir)


def before_scenario(context, _):
    """Setup data that could change during a scenario so each test starts clean."""
    _log.info("setting up scenario...")
    context.etag_manager = ETagManager(context.cache, context.client_config)
    _add_account(context)
    _add_skills(context)
    _add_device(context)
    _add_device_skills(context)
    context.wake_word_files = []
    context.duplicate_hash = False


def after_scenario(context, _):
    """Cleanup data that could change during a scenario so next scenario starts fresh.

    The database is setup with cascading deletes that take care of cleaning up[
    referential integrity for us.  All we have to do here is delete the account
    and all rows on all tables related to that account will also be deleted.
    """
    _log.info("cleaning up after scenario...")
    remove_account(context.db, context.account)
    remove_account_activity(context.db)
    remove_text_to_speech(context.db, context.voice)
    for skill in context.skills.values():
        remove_skill(context.db, skill[0])
    for wake_word_file in context.wake_word_files:
        remove_wake_word_files(context.db, wake_word_file)


def _add_account(context):
    """Add an account object to the context for use in step code."""
    context.account = add_account(context.db)
    add_account_preference(context.db, context.account.id)
    context.geography_id = add_account_geography(context.db, context.account)


def _add_device(context):
    """Add a device object to the context for use in step code."""
    context.voice = add_text_to_speech(context.db)
    device = add_device(context.db, context.account.id, context.geography_id)
    context.device = device
    context.device_id = device["id"]
    context.device_name = "Selene Test Device"
    context.device_login = generate_device_login(device["id"], context.cache)
    context.access_token = context.device_login["accessToken"]


def _add_skills(context):
    """Add skill objects to the context for use in step code."""
    foo_skill, foo_settings_display = add_skill(
        context.db, skill_global_id="foo-skill|19.02",
    )
    bar_skill, bar_settings_display = add_skill(
        context.db,
        skill_global_id="bar-skill|19.02",
        settings_fields=[
            build_label_field(),
            build_text_field(),
            build_checkbox_field(),
        ],
    )
    context.skills = dict(
        foo=(foo_skill, foo_settings_display), bar=(bar_skill, bar_settings_display)
    )


def _add_device_skills(context):
    """Link skills to devices for use in step code."""
    for value in context.skills.values():
        skill, settings_display = value
        context.manifest_skill = add_device_skill(context.db, context.device_id, skill)
        settings_values = None
        if skill.skill_gid.startswith("bar"):
            settings_values = dict(textfield="Device text value", checkboxfield="false")
        add_device_skill_settings(
            context.db,
            context.device_id,
            settings_display,
            settings_values=settings_values,
        )


def after_tag(context, tag):
    """Delete data that was added as a result of running a test with a specified tag."""
    if tag == "new_skill":
        _delete_new_skill(context)
    elif tag == "stt":
        _delete_stt_tagging_files()


def _delete_new_skill(context):
    """Delete a skill that was added during a test."""
    remove_device_skill(context.db, context.new_manifest_skill)
    remove_skill(context.db, context.new_skill)


def _delete_stt_tagging_files():
    """Delete speech to text transcriptions that were added during a test."""
    data_dir = "/opt/selene/data"
    for file_name in os.listdir(data_dir):
        os.remove(os.path.join(data_dir, file_name))
