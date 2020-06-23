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
from datetime import date, datetime

from behave import given, then, when
from hamcrest import (
    assert_that,
    equal_to,
    greater_than,
    has_item,
    is_in,
    none,
    starts_with,
)

from selene.data.account import (
    AccountRepository,
    PRIVACY_POLICY,
    TERMS_OF_USE,
    OPEN_DATASET,
)
from selene.data.metric import AccountActivityRepository
from selene.testing.account_activity import check_account_metrics
from selene.testing.api import (
    generate_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
)
from selene.testing.membership import MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP

BAR_EMAIL_ADDRESS = "bar@mycroft.ai"
STRIPE_METHOD = "Stripe"
VISA_TOKEN = "tok_visa"


@given("an account with a monthly membership")
def add_membership_to_account(context):
    """Use the API to add a monthly membership on Stripe

    The API is used so that the Stripe API can be interacted with.
    """
    context.username = "foo"
    context.access_token = generate_access_token(context)
    set_access_token_cookie(context)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)
    add_membership_via_api(context)


@given("an account without a membership")
def get_account_no_membership(context):
    context.username = "foo"


@given("an account opted {in_or_out} the Open Dataset agreement")
def set_account_open_dataset(context, in_or_out):
    context.username = "foo"
    if in_or_out == "out of":
        account = context.accounts["foo"]
        account_repo = AccountRepository(context.db)
        account_repo.expire_open_dataset_agreement(account.id)


@when("a user requests their profile")
def call_account_endpoint(context):
    context.response = context.client.get(
        "/api/account", content_type="application/json"
    )


@when("a monthly membership is added")
def add_monthly_membership(context):
    context.response = add_membership_via_api(context)


@when("the membership is cancelled")
def cancel_membership(context):
    membership_data = dict(newMembership=False, membershipType=None)
    context.response = context.client.patch(
        "/api/account",
        data=json.dumps(dict(membership=membership_data)),
        content_type="application/json",
    )


def add_membership_via_api(context):
    membership_data = dict(
        newMembership=True,
        membershipType=MONTHLY_MEMBERSHIP,
        paymentMethod=STRIPE_METHOD,
        paymentToken=VISA_TOKEN,
    )
    return context.client.patch(
        "/api/account",
        data=json.dumps(dict(membership=membership_data)),
        content_type="application/json",
    )


@when("the membership is changed to yearly")
def change_to_yearly_account(context):
    membership_data = dict(newMembership=False, membershipType=YEARLY_MEMBERSHIP)
    context.response = context.client.patch(
        "/api/account",
        data=json.dumps(dict(membership=membership_data)),
        content_type="application/json",
    )


@when("the user opts {in_or_out} the open dataset")
def set_open_dataset_status(context, in_or_out):
    if in_or_out not in ("into", "out of"):
        raise ValueError('User can only opt "into" or "out of" the agreement')
    context.response = context.client.patch(
        "/api/account",
        data=json.dumps(dict(openDataset=True if in_or_out == "into" else False)),
        content_type="application/json",
    )


@then("user profile is returned")
def validate_response(context):
    response_data = context.response.json
    utc_date = datetime.utcnow().date()
    account = context.accounts["foo"]
    assert_that(response_data["emailAddress"], equal_to(account.email_address))
    assert_that(response_data["membership"]["type"], equal_to("Monthly Membership"))
    assert_that(response_data["membership"]["duration"], none())
    assert_that(response_data["membership"], has_item("id"))

    assert_that(len(response_data["agreements"]), equal_to(3))
    for agreement in response_data["agreements"]:
        assert_that(
            agreement["type"], is_in([PRIVACY_POLICY, TERMS_OF_USE, OPEN_DATASET])
        )
        assert_that(
            agreement["acceptDate"], equal_to(str(utc_date.strftime("%B %d, %Y")))
        )
        assert_that(agreement, has_item("id"))


@then("the account should have a monthly membership")
def validate_monthly_account(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts["foo"].id
    )
    assert_that(membership.type, equal_to(MONTHLY_MEMBERSHIP))
    assert_that(membership.payment_account_id, starts_with("cus"))
    assert_that(membership.start_date, equal_to(datetime.utcnow().date()))
    assert_that(membership.end_date, none())


@then("the account should have no membership")
def validate_absence_of_membership(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts["foo"].id
    )
    assert_that(membership, none())


@then("the account should have a yearly membership")
def yearly_account(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts["foo"].id
    )
    assert_that(membership.type, equal_to(YEARLY_MEMBERSHIP))
    assert_that(membership.payment_account_id, starts_with("cus"))


@then("the new member will be reflected in the account activity metrics")
def check_new_member_account_metrics(context):
    """Ensure a new membership is accurately reflected in the metrics."""
    check_account_metrics(context, "members", "members_added")


@then("the deleted member will be reflected in the account activity metrics")
def check_expired_member_account_metrics(context):
    """Ensure that the account deletion is recorded in the metrics schema."""
    acct_activity_repository = AccountActivityRepository(context.db)
    account_activity = acct_activity_repository.get_activity_by_date(
        datetime.utcnow().date()
    )
    if context.account_activity is None:
        assert_that(account_activity.members, greater_than(0))
        assert_that(account_activity.members_expired, equal_to(1))
    else:
        # Membership was added in a previous step so rather than the membership being
        # decreased by one, it would net to being the same after the expiration.
        assert_that(
            account_activity.members, equal_to(context.account_activity.members),
        )
        assert_that(
            account_activity.members_expired,
            equal_to(context.account_activity.members_expired + 1),
        )


@then("the account {will_or_wont} have a open dataset agreement")
def check_for_open_dataset_agreement(context, will_or_wont):
    account_repo = AccountRepository(context.db)
    account = account_repo.get_account_by_id(context.accounts["foo"].id)
    agreements = [agreement.type for agreement in account.agreements]
    if will_or_wont == "will":
        assert_that(OPEN_DATASET, is_in(agreements))
    elif will_or_wont == "won't":
        assert_that(OPEN_DATASET, not is_in(agreements))
    else:
        raise ValueError('Valid values are only "will" or "won\'t"')


@then("the new agreement will be reflected in the account activity metrics")
def check_new_member_account_metrics(context):
    """Ensure a new agreement is accurately reflected in the metrics."""
    check_account_metrics(context, "open_dataset", "open_dataset_added")


@then("the deleted agreement will be reflected in the account activity metrics")
def check_new_member_account_metrics(context):
    """Ensure a new agreement is accurately reflected in the metrics."""
    check_account_metrics(context, "open_dataset", "open_dataset_deleted")
