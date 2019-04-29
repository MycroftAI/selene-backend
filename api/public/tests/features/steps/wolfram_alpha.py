from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that


@when('a question is sent')
def send_question(context):
    login = context.device_login
    access_token = login['accessToken']
    context.wolfram_response = context.client.get(
        '/v1/wa?input=what+is+the+capital+of+Brazil',
        headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    )


@then('the wolfram alpha endpoint should return 200')
def validate_response(context):
    response = context.wolfram_response
    assert_that(response.status_code, HTTPStatus.OK)
