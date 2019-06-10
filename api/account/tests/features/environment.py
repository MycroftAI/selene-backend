from behave import fixture, use_fixture

from account_api.api import acct
from selene.data.account import (
    AccountRepository,
)
from selene.testing import (
    add_account,
    add_account_geography,
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


def before_all(context):
    use_fixture(acct_api_client, context)
    context.db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    context.terms_of_use, context.privacy_policy = add_agreements(context.db)


def after_all(context):
    remove_agreements(
        context.db,
        [context.privacy_policy, context.terms_of_use]
    )


def before_scenario(context, _):
    context.account = context.foo_account = add_account(context.db)
    context.geography_id = add_account_geography(context.db, context.account)


def after_scenario(context, _):
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    _delete_account(context, db)
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


def _clean_cache():
    cache = SeleneCache()
    cache.delete('pairing.token:this is a token')
