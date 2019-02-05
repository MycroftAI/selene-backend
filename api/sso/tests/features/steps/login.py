from binascii import b2a_base64
from http import HTTPStatus
from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item

from selene.account import AccountRepository
from selene.util.db import get_db_connection


@given('user enters email address "{email}" and password "{password}"')
def save_credentials(context, email, password):
    context.email = email
    context.password = password


@given('user "{email}" authenticates through facebook')
@given('user "{email}" is authenticated')
def save_email(context, email):
    context.email = email


@when('single sign on validates the account')
def call_validate_federated_endpoint(context):
    context.response = context.client.post(
        '/api/validate-federated',
        data=dict(email=context.email)
    )


@when('user attempts to login')
def call_internal_login_endpoint(context):
    credentials = '{}:{}'.format(context.email, context.password).encode()
    credentials = b2a_base64(credentials, newline=False).decode()
    context.response = context.client.get(
        '/api/internal-login',
        headers=dict(Authorization='Basic ' + credentials))


@then('login succeeds')
def check_for_login_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    for cookie in context.response.headers.getlist('Set-Cookie'):
        ingredients = parse_cookie(cookie)
        ingredient_names = list(ingredients.keys())
        if cookie.startswith('seleneAccess'):
            assert_that(ingredient_names, has_item('seleneAccess'))
        elif cookie.startswith('seleneRefresh'):
            assert_that(ingredient_names, has_item('seleneRefresh'))
            context.refresh_token = ingredients['seleneRefresh']
        else:
            raise ValueError('unexpected cookie found: ' + cookie)
        for ingredient_name in ('Domain', 'Expires', 'Max-Age'):
            assert_that(ingredient_names, has_item(ingredient_name))
    with get_db_connection(context.db_pool) as db:
        acct_repository = AccountRepository(db)
        account = acct_repository.get_account_by_email(context.email)
    assert_that(account.refresh_tokens, has_item(context.refresh_token))


@then('login fails with "{error_message}" error')
def check_for_login_fail(context, error_message):
    assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    assert_that(context.response.get_json(), equal_to(error_message))


def parse_cookie(cookie: str) -> dict:
    ingredients = {}
    for ingredient in cookie.split('; '):
        if '=' in ingredient:
            key, value = ingredient.split('=')
            ingredients[key] = value
        else:
            ingredients[ingredient] = None

    return ingredients
