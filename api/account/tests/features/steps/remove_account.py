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

import os

import stripe
from behave import then, when
from hamcrest import assert_that, equal_to
from stripe.error import InvalidRequestError

from selene.data.account import AccountRepository


@when('the user\'s account is deleted')
def account_deleted(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts['foo'].id
    )
    context.accounts['foo'].membership = membership
    context.response = context.client.delete('/api/account')


@then('the membership is removed from stripe')
def check_stripe(context):
    account = context.accounts['foo']
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    subscription_not_found = False
    try:
        stripe.Subscription.retrieve(account.membership.payment_account_id)
    except InvalidRequestError:
        subscription_not_found = True
    assert_that(subscription_not_found, equal_to(True))
