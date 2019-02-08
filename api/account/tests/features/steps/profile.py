from http import HTTPStatus
import json

from behave import given, then, when
from hamcrest import assert_that, equal_to

from selene.api.testing import generate_auth_tokens


@given('an authenticated user')
def setup_authenticated_user(context):
    generate_auth_tokens(context)


@when('account endpoint is called to get user profile')
def call_account_endpoint(context):
    context.response = context.client.get('/api/account')


@then('user profile is returned')
def validate_response(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(context.response.data)
    print(response_data)

