from binascii import b2a_base64
from http import HTTPStatus
import json
from unittest.mock import patch

from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item

from selene.api.testing import get_account, validate_token_cookies

VALIDATE_FEDERATED = 'sso_api.endpoints.validate_federated.'


@given('user enters email address "{email}" and password "{password}"')
def save_credentials(context, email, password):
    context.email = email
    context.password = password


@given('user "{email}" authenticates through facebook')
def save_email(context, email):
    context.email = email


@when('single sign on validates the account')
def call_validate_federated_endpoint(context):
    func_to_patch = VALIDATE_FEDERATED + 'get_facebook_account_email'
    with patch(func_to_patch, return_value=context.email):
        context.response = context.client.post(
            '/api/validate-federated',
            data=json.dumps(dict(platform='Facebook', token='facebook_token')),
            content_type='application/json'
        )


@when('user attempts to login')
def call_internal_login_endpoint(context):
    credentials = '{}:{}'.format(context.email, context.password).encode()
    credentials = b2a_base64(credentials, newline=False).decode()
    context.response = context.client.get(
        '/api/internal-login',
        headers=dict(Authorization='Basic ' + credentials))


@then('login request succeeds')
def check_for_login_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )


@then('response contains authentication tokens')
def check_token_cookies(context):
    validate_token_cookies(context)


@then('login fails with "{error_message}" error')
def check_for_login_fail(context, error_message):
    assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    assert_that(
        context.response.headers['Access-Control-Allow-Origin'],
        equal_to('*')
    )
    assert_that(context.response.is_json, equal_to(True))
    response_json = context.response.get_json()
    assert_that(response_json['error'], equal_to(error_message))
