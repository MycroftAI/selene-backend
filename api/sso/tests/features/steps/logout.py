from http import HTTPStatus
from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item, is_not

from selene.data.account import RefreshTokenRepository
from selene.api.testing import get_account, validate_token_cookies
from selene.util.auth import AuthenticationTokenGenerator
from selene.util.db import get_db_connection

ACCESS_TOKEN_COOKIE_KEY = 'seleneAccess'
REFRESH_TOKEN_COOKIE_KEY = 'seleneRefresh'


@given('user "{email}" is authenticated')
def save_email(context, email):
    context.email = email


@when('user attempts to logout')
def call_logout_endpoint(context):
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
        token_repository = RefreshTokenRepository(db, context.account)
        token_repository.add_refresh_token(token_generator.refresh_token)

    context.response = context.client.get('/api/logout')


@then('request is successful')
def check_for_logout_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )


@then('response contains expired token cookies')
def check_response_cookies(context):
    validate_token_cookies(context, expired=True)


@then('refresh token in request is removed from account')
def check_refresh_token_removed(context):
    account = get_account(context)
    assert_that(
        account.refresh_tokens,
        is_not(has_item(context.request_refresh_token))
    )


@then('logout fails with "{error_message}" error')
def check_for_login_fail(context, error_message):
    assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    assert_that(context.response.get_json(), equal_to(error_message))
