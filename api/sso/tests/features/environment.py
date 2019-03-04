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
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
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
            payment_account_id='foo'
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
    with get_db_connection(context.db_pool) as db:
        acct_repository = AccountRepository(db)
        acct_repository.remove(context.account)
        agreement_repository = AgreementRepository(db)
        agreement_repository.remove(context.agreement, testing=True)
