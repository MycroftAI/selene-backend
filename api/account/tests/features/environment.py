from datetime import date, timedelta
import os

from behave import fixture, use_fixture

from account_api.api import acct
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountSubscription,
    Agreement,
    AgreementRepository,
    PRIVACY_POLICY
)
from selene.util.db import get_db_connection


@fixture
def acct_api_client(context):
    acct.testing = True
    context.client_config = acct.config
    context.client = acct.test_client()

    yield context.client


def before_feature(context, _):
    use_fixture(acct_api_client, context)
    os.environ['SALT'] = 'testsalt'


def before_scenario(context, _):

    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        _add_agreement(context, db)
        _add_account(context, db)


def _add_agreement(context, db):
    context.agreement = Agreement(
        type='Privacy Policy',
        version='1',
        content='this is Privacy Policy version 1',
        effective_date=date.today() - timedelta(days=5)
    )
    agreement_repository = AgreementRepository(db)
    agreement_repository.add(context.agreement)


def _add_account(context, db):
    test_account = Account(
        id=None,
        email_address='foo@mycroft.ai',
        username='foobar',
        refresh_tokens=None,
        subscription=AccountSubscription(
            type='monthly supporter',
            start_date=None,
            stripe_customer_id='foo'
        ),
        agreements=[
            AccountAgreement(name=PRIVACY_POLICY, accept_date=None)
        ]
    )

    acct_repository = AccountRepository(db)
    acct_repository.add(test_account, 'foo')
    context.account = acct_repository.get_account_by_email(
        test_account.email_address
    )


def after_scenario(context, _):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        acct_repository.remove(context.account)
        agreement_repository = AgreementRepository(db)
        agreement_repository.remove(context.agreement, testing=True)
