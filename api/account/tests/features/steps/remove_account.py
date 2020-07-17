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
"""Step functions for the account deletion functionality in the single sign on API"""
import os
from datetime import datetime

import stripe
from behave import then, when  # pylint: disable=no-name-in-module
from hamcrest import assert_that, equal_to
from stripe.error import InvalidRequestError

from selene.data.account import AccountRepository
from selene.data.metric import AccountActivityRepository


@when("the user's account is deleted")
def account_deleted(context):
    """Ensure account no longer exists in database."""
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts["foo"].id
    )
    context.accounts["foo"].membership = membership
    context.response = context.client.delete("/api/account")


@then("the membership is removed from stripe")
def check_stripe(context):
    """Ensure an account with a membership is no longer charged."""
    account = context.accounts["foo"]
    stripe.api_key = os.environ["STRIPE_PRIVATE_KEY"]
    subscription_not_found = False
    try:
        stripe.Subscription.retrieve(account.membership.payment_account_id)
    except InvalidRequestError:
        subscription_not_found = True
    assert_that(subscription_not_found, equal_to(True))


@then("the deleted account will be reflected in the account activity metrics")
def check_db_for_account_metrics(context):
    """Ensure that the account deletion is recorded in the metrics schema."""
    acct_activity_repository = AccountActivityRepository(context.db)
    account_activity = acct_activity_repository.get_activity_by_date(
        datetime.utcnow().date()
    )
    if context.account_activity is None:
        assert_that(account_activity.accounts_deleted, equal_to(1))
    else:
        assert_that(
            account_activity.accounts_deleted,
            equal_to(context.account_activity.accounts_deleted + 1),
        )
