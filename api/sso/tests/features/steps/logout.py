from http import HTTPStatus
from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item, is_not

from selene.api.testing import (
    generate_auth_tokens,
    get_account,
    validate_token_cookies
)


@given('user "{email}" is authenticated')
def save_email(context, email):
    context.email = email


@when('user attempts to logout')
def call_logout_endpoint(context):
    generate_auth_tokens(context)
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