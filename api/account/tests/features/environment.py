import os

from behave import fixture, use_fixture

from account_api.api import acct
from selene.data.account import AccountRepository
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
        acct_repository = AccountRepository(db)
        account_id = acct_repository.add('foo@mycroft.ai', 'foo')
        account = acct_repository.get_account_by_id(account_id)
    context.account = account


def after_scenario(context, _):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        acct_repository.remove(context.account)
