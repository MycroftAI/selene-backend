import os

from behave import fixture, use_fixture

from sso_api.api import sso
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountSubscription
)
from selene.util.db import get_db_connection


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
    test_account = Account(
        id=None,
        email_address='foo@mycroft.ai',
        refresh_tokens=None,
        subscription=AccountSubscription(
            type='monthly supporter',
            start_date=None,
            stripe_customer_id='foo'
        ),
        agreements=[
            AccountAgreement(name='terms', signature_date=None)
        ]
    )
    with get_db_connection(
            context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        acct_repository.add(test_account, 'foo')
        context.account = acct_repository.get_account_by_email(
            test_account.email_address
        )


def after_scenario(context, _):
    with get_db_connection(context.db_pool) as db:
        acct_repository = AccountRepository(db)
        acct_repository.remove(context.account)
