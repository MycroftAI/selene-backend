import json
from binascii import b2a_base64
from behave import given, when


@given('a user who authenticates with a password')
def setup_user(context):
    acct = context.accounts['foobar']
    context.email = acct.email_address
    context.password = 'bar'
    context.change_password_request = dict(
        accountId=acct.id, password=b2a_base64(b'bar').decode()
    )


@when('the user changes their password')
def call_password_change_endpoint(context):
    context.client.content_type = 'application/json'
    response = context.client.put(
        '/api/password-change',
        data=json.dumps(context.change_password_request),
        content_type='application/json'
    )
    context.response = response
