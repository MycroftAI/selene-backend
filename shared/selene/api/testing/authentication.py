from hamcrest import assert_that, equal_to, has_item

from selene.data.account import (
    Account,
    AccountRepository,
    RefreshTokenRepository
)
from selene.util.auth import AuthenticationTokenGenerator
from selene.util.db import get_db_connection

ACCESS_TOKEN_COOKIE_KEY = 'seleneAccess'
REFRESH_TOKEN_COOKIE_KEY = 'seleneRefresh'


def generate_auth_tokens(context):
    token_generator = AuthenticationTokenGenerator(
        context.account.id,
        context.client_config['ACCESS_SECRET'],
        context.client_config['REFRESH_SECRET']
    )
    context.client.set_cookie(
        context.client_config['DOMAIN'],
        ACCESS_TOKEN_COOKIE_KEY,
        token_generator.access_token
    )
    context.client.set_cookie(
        context.client_config['DOMAIN'],
        REFRESH_TOKEN_COOKIE_KEY,
        token_generator.refresh_token
    )
    context.request_refresh_token = token_generator.refresh_token

    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        token_repository = RefreshTokenRepository(db, context.account.id)
        token_repository.add_refresh_token(token_generator.refresh_token)


def validate_token_cookies(context, expired=False):
    for cookie in context.response.headers.getlist('Set-Cookie'):
        ingredients = _parse_cookie(cookie)
        ingredient_names = list(ingredients.keys())
        if ACCESS_TOKEN_COOKIE_KEY in ingredient_names:
            context.access_token = ingredients[ACCESS_TOKEN_COOKIE_KEY]
        elif REFRESH_TOKEN_COOKIE_KEY in ingredient_names:
            context.refresh_token = ingredients[REFRESH_TOKEN_COOKIE_KEY]
        for ingredient_name in ('Domain', 'Expires', 'Max-Age'):
            assert_that(ingredient_names, has_item(ingredient_name))
        if expired:
            assert_that(ingredients['Max-Age'], equal_to('0'))

    assert hasattr(context, 'access_token'), 'no access token in response'
    assert hasattr(context, 'refresh_token'), 'no refresh token in response'
    if expired:
        assert_that(context.access_token, equal_to(''))
        assert_that(context.refresh_token, equal_to(''))


def _parse_cookie(cookie: str) -> dict:
    ingredients = {}
    for ingredient in cookie.split('; '):
        if '=' in ingredient:
            key, value = ingredient.split('=')
            ingredients[key] = value
        else:
            ingredients[ingredient] = None

    return ingredients


def get_account(context) -> Account:
    with get_db_connection(context.db_pool) as db:
        acct_repository = AccountRepository(db)
        account = acct_repository.get_account_by_id(context.account.id)

    return account
