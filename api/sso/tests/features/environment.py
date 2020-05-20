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
"""Environmental controls for the single sign on API tests."""
import os

from behave import fixture, use_fixture

from sso_api.api import sso
from selene.testing.account import add_account, remove_account
from selene.testing.agreement import add_agreements, remove_agreements
from selene.util.db import connect_to_db


@fixture
def sso_client(context):
    """Setup a test fixture for the single-sign-on api."""
    sso.testing = True
    context.db_pool = sso.config["DB_CONNECTION_POOL"]
    context.client_config = sso.config
    context.client = sso.test_client()

    yield context.client


def before_all(context):
    """Global setup to run before any tests."""
    use_fixture(sso_client, context)
    os.environ["SALT"] = "testsalt"
    context.db = connect_to_db(context.client_config["DB_CONNECTION_CONFIG"])
    add_agreements(context)


def before_scenario(context, _):
    """Scenario-level setup."""
    account = add_account(context.db, password="foo")
    context.accounts = dict(foobar=account)


def after_scenario(context, _):
    """Scenario-level cleanup.

    The database is setup with cascading deletes that take care of cleaning up[
    referential integrity for us.  All we have to do here is delete the account
    and all rows on all tables related to that account will also be deleted.
    """
    for account in context.accounts.values():
        remove_account(context.db, account)


def after_all(context):
    """Global cleanup steps run after all tests complete."""
    remove_agreements(
        context.db, [context.privacy_policy, context.terms_of_use, context.open_dataset]
    )
