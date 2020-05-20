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
"""Step functions for adding an account via the single sign on API."""
from binascii import b2a_base64
from datetime import datetime

from behave import given, then, when  # pylint: disable=no-name-in-module
from flask import json
from hamcrest import assert_that, equal_to, is_in, not_none

from selene.data.account import AccountRepository, PRIVACY_POLICY, TERMS_OF_USE
from selene.data.metric import AccountActivityRepository


@given("a user completes new account setup")
def build_new_account_request(context):
    """Build base request data for the new account tests."""
    context.new_account_request = dict(
        termsOfUse=True,
        privacyPolicy=True,
        login=dict(
            federatedPlatform=None,
            federatedToken=None,
            email=b2a_base64(b"bar@mycroft.ai").decode(),
            password=b2a_base64(b"bar").decode(),
        ),
    )


@given("user does not include {required_field}")
def remove_required_field(context, required_field):
    """Remove the specified field from the new account request."""
    if required_field == "an email address":
        del context.new_account_request["login"]["email"]
    elif required_field == "a password":
        del context.new_account_request["login"]["password"]
    elif required_field == "an accepted Terms of Use":
        del context.new_account_request["termsOfUse"]
    elif required_field == "an accepted Privacy Policy":
        del context.new_account_request["privacyPolicy"]


@given("user does not agree to the {agreement}")
def reject_agreement(context, agreement):
    """Set the status of the specified agreement to rejected."""
    if agreement == "Terms of Use":
        context.new_account_request["termsOfUse"] = False
    elif agreement == "Privacy Policy":
        context.new_account_request["privacyPolicy"] = False


@when("the new account request is submitted")
def call_add_account_endpoint(context):
    """Call the single sign on API endpoint to create a new account"""
    context.client.content_type = "application/json"
    response = context.client.post(
        "/api/account",
        data=json.dumps(context.new_account_request),
        content_type="application/json",
    )
    context.response = response


@then("the account will be added to the system")
def check_db_for_account(context):
    """Check that the account was created as expected."""
    acct_repository = AccountRepository(context.db)
    account = acct_repository.get_account_by_email("bar@mycroft.ai")
    # add account to context so it will deleted by cleanup step
    context.accounts["bar"] = account
    assert_that(account, not_none())
    assert_that(account.email_address, equal_to("bar@mycroft.ai"))

    assert_that(len(account.agreements), equal_to(2))
    utc_date = datetime.utcnow().date()
    for agreement in account.agreements:
        assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
        assert_that(agreement.accept_date, equal_to(str(utc_date)))


@then("the new account will be reflected in the account activity metrics")
def check_db_for_account_metrics(context):
    """Ensure the new account is accurately reflected in the metrics."""
    acct_activity_repository = AccountActivityRepository(context.db)
    account_activity = acct_activity_repository.get_activity_by_date(
        datetime.utcnow().date()
    )
    if context.account_activity is None:
        assert_that(account_activity.accounts_added, equal_to(1))
    else:
        assert_that(
            account_activity.accounts_added,
            equal_to(context.account_activity.accounts_added + 1),
        )
