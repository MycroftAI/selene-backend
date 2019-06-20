from http import HTTPStatus
from datetime import datetime

from behave import given, then
from hamcrest import assert_that, equal_to, is_in, not_none

from selene.util.cache import DEVICE_LAST_CONTACT_KEY


@then('device last contact timestamp is updated')
def check_device_last_contact(context):
    key = DEVICE_LAST_CONTACT_KEY.format(device_id=context.device_id)
    value = context.cache.get(key).decode()
    assert_that(value, not_none())

    last_contact_ts = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    assert_that(last_contact_ts.date(), equal_to(datetime.utcnow().date()))


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


@given('an authorized device')
def build_request_header(context):
    context.request_header = dict(
        Authorization='Bearer {token}'.format(token=context.access_token)
    )


@given('an unauthorized device')
def build_unauthorized_request_header(context):
    context.request_header = dict(
        Authorization='Bearer {token}'.format(token='bogus_token')
    )
