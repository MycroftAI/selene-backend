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

from datetime import date
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountMembership,
    AccountRepository,
    OPEN_DATASET,
    PRIVACY_POLICY,
    TERMS_OF_USE,
)


def build_test_account(**overrides):
    test_agreements = [
        AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
        AccountAgreement(type=TERMS_OF_USE, accept_date=date.today()),
        AccountAgreement(type=OPEN_DATASET, accept_date=date.today()),
    ]
    return Account(
        email_address=overrides.get("email_address") or "foo@mycroft.ai",
        username=overrides.get("username") or "foobar",
        agreements=overrides.get("agreements") or test_agreements,
    )


def add_account(db, **overrides):
    acct_repository = AccountRepository(db)
    account = build_test_account(**overrides)
    password = overrides.get("password") or "test_password"
    account.id = acct_repository.add(account, password)
    if account.membership is not None:
        acct_repository.add_membership(account.id, account.membership)

    return account


def remove_account(db, account):
    account_repository = AccountRepository(db)
    account_repository.remove(account)


def build_test_membership(**overrides):
    stripe_acct = "test_stripe_acct_id"
    return AccountMembership(
        type=overrides.get("type") or "Monthly Membership",
        start_date=overrides.get("start_date") or date.today(),
        payment_method=overrides.get("payment_method") or "Stripe",
        payment_account_id=overrides.get("payment_account_id") or stripe_acct,
        payment_id=overrides.get("payment_id") or "test_stripe_payment_id",
    )


def add_account_membership(db, account_id, **overrides):
    membership = build_test_membership(**overrides)
    acct_repository = AccountRepository(db)
    acct_repository.add_membership(account_id, membership)

    return membership
