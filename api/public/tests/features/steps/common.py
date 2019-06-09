from http import HTTPStatus

from behave import then
from hamcrest import assert_that, equal_to, is_in


@then('the request will be successful')
def check_request_success(context):
    assert_that(
        context.response.status_code,
        is_in([HTTPStatus.OK, HTTPStatus.NO_CONTENT])
    )


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
