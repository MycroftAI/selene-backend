from http import HTTPStatus

from behave import given, then
from hamcrest import assert_that, equal_to

from selene.api.testing import generate_access_token, generate_refresh_token


@given('an authenticated user')
def setup_authenticated_user(context):
    generate_access_token(context)
    generate_refresh_token(context)


@then('the request will be successful')
def check_request_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))


@then('the request will fail with {error_type} error')
def check_for_bad_request(context, error_type):
    if error_type == 'a bad request':
        assert_that(
            context.response.status_code,
            equal_to(HTTPStatus.BAD_REQUEST)
        )
    elif error_type == 'an unauthorized':
        assert_that(
            context.response.status_code,
            equal_to(HTTPStatus.UNAUTHORIZED)
        )
    else:
        raise ValueError('unsupported error_type')
