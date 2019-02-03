from binascii import b2a_base64
from http import HTTPStatus
from behave import given, then, when
from hamcrest import assert_that, contains, equal_to, has_item

from selene.account import Account, AccountRepository


# TODO: add a step here when the add account logic is built
@given('user enters email address "{user}" and password "{password}"')
def add_credentials_to_db(context, user, password):
    context.user = user
    context.password = password


@when('user attempts to login')
def call_internal_login_endpoint(context):
    credentials = '{}:{}'.format(context.user, context.password).encode()
    credentials = b2a_base64(credentials, newline=False).decode()
    context.response = context.client.get(
        '/api/login/internal',
        headers=dict(Authorization='Basic ' + credentials))


@then('login succeeds')
def check_for_login_success(context):
    assert_that(context.response.status_code, equal_to(200))
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
        else:
            raise ValueError('unexpected cookie found: ' + cookie)
        for ingredient_name in ('Domain', 'Expires', 'Max-Age', 'HttpOnly'):
            assert_that(ingredient_names, has_item(ingredient_name))


@then('login fails')
def check_for_login_fail(context):
    assert_that(context.response.status_code, equal_to(401))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    assert_that(
        context.response.get_json(),
        equal_to('provided credentials not found')
    )


def parse_cookie(cookie: str) -> dict:
    ingredients = {}
    for ingredient in cookie.split('; '):
        if '=' in ingredient:
            key, value = ingredient.split('=')
            ingredients[key] = value
        else:
            ingredients[ingredient] = None

    return ingredients
