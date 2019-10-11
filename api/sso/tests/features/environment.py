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

from datetime import date, timedelta
import os

from behave import fixture, use_fixture

from sso_api.api import sso
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountMembership,
    Agreement,
    AgreementRepository,
    PRIVACY_POLICY
)
from selene.util.db import connect_to_db


@fixture
def sso_client(context):
    sso.testing = True
    context.db_pool = sso.config['DB_CONNECTION_POOL']
    context.client_config = sso.config
    context.client = sso.test_client()

    yield context.client


def before_feature(context, _):
    use_fixture(sso_client, context)
    os.environ['SALT'] = 'testsalt'


def before_scenario(context, _):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    _add_agreement(context, db)
    _add_account(context, db)


def _add_agreement(context, db):
    agreement = Agreement(
        type='Privacy Policy',
        version='999',
        content='this is Privacy Policy version 999',
        effective_date=date.today() - timedelta(days=5)
    )
    agreement_repository = AgreementRepository(db)
    agreement_repository.add(agreement)
    context.agreement = agreement_repository.get_active_for_type(PRIVACY_POLICY)


def _add_account(context, db):
    test_account = Account(
        email_address='foo@mycroft.ai',
        username='foobar',
        membership=AccountMembership(
            type='Monthly Membership',
            start_date=date.today(),
            payment_method='Stripe',
            payment_account_id='foo',
            payment_id='bar'
        ),
        agreements=[
            AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today())
        ]
    )
    acct_repository = AccountRepository(db)
    acct_repository.add(test_account, 'foo')
    context.account = acct_repository.get_account_by_email(
        test_account.email_address
    )


def after_scenario(context, _):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    acct_repository = AccountRepository(db)
    acct_repository.remove(context.account)
    agreement_repository = AgreementRepository(db)
    agreement_repository.remove(context.agreement, testing=True)
