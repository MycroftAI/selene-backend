from behave import given, then
from hamcrest import assert_that, equal_to, is_not

from selene.api.testing import (
    generate_access_token,
    generate_refresh_token,
    validate_token_cookies
)
from selene.data.account import AccountRepository
from selene.util.auth import AuthenticationToken
from selene.util.db import connect_to_db


@given('an authenticated user with an expired access token')
def generate_refresh_token_only(context):
    generate_access_token(context, expire=True)
    generate_refresh_token(context)
    context.old_refresh_token = context.refresh_token.jwt


@given('a previously authenticated user with expired tokens')
def expire_both_tokens(context):
    generate_access_token(context, expire=True)
    generate_refresh_token(context, expire=True)


@then('the authentication tokens will remain unchanged')
def check_for_no_new_cookie(context):
    cookies = context.response.headers.getlist('Set-Cookie')
    assert_that(cookies, equal_to([]))


@then('the authentication tokens will be refreshed')
def check_for_new_cookies(context):
    validate_token_cookies(context)
    assert_that(
        context.refresh_token,
        is_not(equal_to(context.old_refresh_token))
    )
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    acct_repository = AccountRepository(db)
    account = acct_repository.get_account_by_id(context.account.id)

    refresh_token = AuthenticationToken(
        context.client_config['REFRESH_SECRET'],
        0
    )
    refresh_token.jwt = context.refresh_token
    refresh_token.validate()
    assert_that(refresh_token.is_valid, equal_to(True))
    assert_that(refresh_token.is_expired, equal_to(False))
    assert_that(refresh_token.account_id, equal_to(account.id))
