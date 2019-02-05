from behave import fixture, use_fixture

from sso_api.api import sso
from selene.account import RefreshTokenRepository
from selene.util.db import get_db_connection


@fixture
def sso_client(context):
    sso.testing = True
    context.db_pool = sso.config['DB_CONNECTION_POOL']
    context.client = sso.test_client()

    yield context.client


def before_feature(context, _):
    use_fixture(sso_client, context)


def after_scenario(context, _):
    if hasattr(context, 'refresh_token'):
        with get_db_connection(context.db_pool) as db:
            token_repository = RefreshTokenRepository(db, context.account)
            token_repository.delete_refresh_token(context.refresh_token)
