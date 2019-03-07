import json
import uuid
from http import HTTPStatus
from unittest.mock import patch, MagicMock

from behave import when, then
from hamcrest import assert_that, equal_to

email_request = dict(
    title='this is a test',
    sender='test@test.com',
    body='body message'
)


@when('an email message is sent to the email endpoint')
@patch('smtplib.SMTP')
def send_email(context, email_client):
    context.client_config['EMAIL_CLIENT'] = email_client
    device_id = context.device_login['uuid']
    context.email_response = context.client.post(
        '/device/{uuid}/email'.format(uuid=device_id),
        data=json.dumps(email_request),
        content_type='application_json'
    )


@then('an email should be sent to the user\'s account that owns the device')
def validate_response(context):
    response = context.email_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    email_client: MagicMock = context.client_config['EMAIL_CLIENT']
    email_client.send_message.assert_called()


@when('the email endpoint is called for a nonexistent device')
@patch('smtplib.SMTP')
def send_email_invalid_device(context, email_client):
    context.client_config['EMAIL_CLIENT'] = email_client
    context.email_invalid_response = context.client.post(
        '/device/{uuid}/email'.format(uuid=str(uuid.uuid4())),
        data=json.dumps(email_request),
        content_type='application_json'
    )


@then('204 status code should be returned')
def validate_response_invalid_device(context):
    response = context.email_invalid_response
    assert_that(response.status_code, equal_to(HTTPStatus.NO_CONTENT))
    email_client: MagicMock = context.client_config['EMAIL_CLIENT']
    email_client.send_message.assert_not_called()
