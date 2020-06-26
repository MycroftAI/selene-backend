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
from selene.testing.text_to_speech import add_text_to_speech, remove_text_to_speech
from selene.testing.wake_word import add_wake_word, remove_wake_word
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db


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
    use_fixture(public_api_client, context)
    context.cache = SeleneCache()
    context.db = connect_to_db(context.client_config["DB_CONNECTION_CONFIG"])
    add_agreements(context)


def after_all(context):
    """Clean up static test data after all tests have run.

    This is data that does not change from test to test so it only needs to be setup
    and torn down once.
    """
    remove_agreements(
        context.db, [context.privacy_policy, context.terms_of_use, context.open_dataset]
    )


def before_scenario(context, _):
    """Setup data that could change during a scenario so each test starts clean."""
    context.etag_manager = ETagManager(context.cache, context.client_config)
    _add_account(context)
    _add_skills(context)
    _add_device(context)
    _add_device_skills(context)


def after_scenario(context, _):
    """Cleanup data that could change during a scenario so next scenario starts fresh.

    The database is setup with cascading deletes that take care of cleaning up[
    referential integrity for us.  All we have to do here is delete the account
    and all rows on all tables related to that account will also be deleted.
    """
    remove_account(context.db, context.account)
    remove_account_activity(context.db)
    remove_wake_word(context.db, context.wake_word)
    remove_text_to_speech(context.db, context.voice)
    for skill in context.skills.values():
        remove_skill(context.db, skill[0])


def _add_account(context):
    """Add an account object to the context for use in step code."""
    context.account = add_account(context.db)
    add_account_preference(context.db, context.account.id)
    context.geography_id = add_account_geography(context.db, context.account)


def _add_device(context):
    """Add a device object to the context for use in step code."""
    context.wake_word = add_wake_word(context.db)
    context.voice = add_text_to_speech(context.db)
    device_id = add_device(context.db, context.account.id, context.geography_id)
    context.device_id = device_id
    context.device_name = "Selene Test Device"
    context.device_login = generate_device_login(device_id, context.cache)
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
