from datetime import date, timedelta

from behave import fixture, use_fixture

from account_api.api import acct
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountMembership,
    Agreement,
    AgreementRepository,
    PRIVACY_POLICY,
    TERMS_OF_USE
)
from selene.data.device import Geography, GeographyRepository
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db


@fixture
def acct_api_client(context):
    acct.testing = True
    context.client_config = acct.config
    context.client = acct.test_client()

    yield context.client


def before_feature(context, _):
    use_fixture(acct_api_client, context)


def before_scenario(context, _):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    _add_agreements(context, db)
    _add_account(context, db)
    _add_geography(context, db)


def _add_agreements(context, db):
    context.privacy_policy = Agreement(
        type=PRIVACY_POLICY,
        version='999',
        content='this is Privacy Policy version 999',
        effective_date=date.today() - timedelta(days=5)
    )
    context.terms_of_use = Agreement(
        type=TERMS_OF_USE,
        version='999',
        content='this is Terms of Use version 999',
        effective_date=date.today() - timedelta(days=5)
    )
    agreement_repository = AgreementRepository(db)
    agreement_id = agreement_repository.add(context.privacy_policy)
    context.privacy_policy.id = agreement_id
    agreement_id = agreement_repository.add(context.terms_of_use)
    context.terms_of_use.id = agreement_id


def _add_account(context, db):
    context.account = Account(
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
    account_id = acct_repository.add(context.account, 'foo')
    context.account.id = account_id


def _add_geography(context, db):
    geography = Geography(
        country='United States',
        region='Missouri',
        city='Kansas City',
        time_zone='America/Chicago'
    )
    geo_repository = GeographyRepository(db, context.account.id)
    context.geography_id = geo_repository.add(geography)


def after_scenario(context, _):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    _delete_account(context, db)
    _delete_agreements(context, db)
    _clean_cache()


def _delete_account(context, db):
    acct_repository = AccountRepository(db)
    acct_repository.remove(context.account)
    bar_acct = acct_repository.get_account_by_email('bar@mycroft.ai')
    if bar_acct is not None:
        acct_repository.remove(bar_acct)
    foo_acct = acct_repository.get_account_by_email('foo@mycroft.ai')
    if foo_acct is not None:
        acct_repository.remove(foo_acct)
    test_acct = acct_repository.get_account_by_email('test@mycroft.ai')
    if test_acct is not None:
        acct_repository.remove(test_acct)


def _delete_agreements(context, db):
    agreement_repository = AgreementRepository(db)
    agreement_repository.remove(context.privacy_policy, testing=True)
    agreement_repository.remove(context.terms_of_use, testing=True)


def _clean_cache():
    cache = SeleneCache()
    cache.delete('pairing.token:this is a token')
