from datetime import date
from http import HTTPStatus
import json

from behave import then, when
from hamcrest import assert_that, equal_to, has_item, none

from selene.data.account import PRIVACY_POLICY


@when('a user requests their profile')
def call_account_endpoint(context):
    context.response = context.client.get('/api/account')


@then('user profile is returned')
def validate_response(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(context.response.data)
    assert_that(
        response_data['emailAddress'],
        equal_to(context.account.email_address)
    )
    assert_that(
        response_data['membership']['type'],
        equal_to('Monthly Membership')
    )
    assert_that(response_data['membership']['duration'], none())
    assert_that(
        response_data['membership'], has_item('id')
    )

    assert_that(len(response_data['agreements']), equal_to(1))
    agreement = response_data['agreements'][0]
    assert_that(agreement['type'], equal_to(PRIVACY_POLICY))
    assert_that(
        agreement['acceptDate'],
        equal_to(str(date.today().strftime('%B %d, %Y')))
    )
    assert_that(agreement, has_item('id'))
