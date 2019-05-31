from datetime import date, timedelta

from behave import fixture, use_fixture

from account_api.api import acct
from selene.data.account import (
    AccountAgreement,
    AccountRepository,
    AccountMembership,
    Agreement,
    AgreementRepository,
    PRIVACY_POLICY,
    TERMS_OF_USE
)
from selene.data.device import Geography, GeographyRepository
from selene.testing import (
    add_account,
    add_agreements,
    remove_account,
    remove_agreements
)
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
    context.terms_of_use, context.privacy_policy = add_agreements(db)
    context.account = context.foo_account = add_account(db)
    _add_geography(context, db)


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
    remove_agreements(db, [context.privacy_policy, context.terms_of_use])
    _clean_cache()


def _delete_account(context, db):
    acct_repository = AccountRepository(db)
    remove_account(db, context.foo_account)
    bar_acct = acct_repository.get_account_by_email('bar@mycroft.ai')
    if bar_acct is not None:
        remove_account(db, bar_acct)
    test_acct = acct_repository.get_account_by_email('test@mycroft.ai')
    if test_acct is not None:
        remove_account(db, test_acct)


def _delete_agreements(context, db):
    agreement_repository = AgreementRepository(db)
    agreement_repository.remove(context.privacy_policy, testing=True)
    agreement_repository.remove(context.terms_of_use, testing=True)


def _clean_cache():
    cache = SeleneCache()
    cache.delete('pairing.token:this is a token')
