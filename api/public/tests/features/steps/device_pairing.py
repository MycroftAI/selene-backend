import json
import uuid
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key

from selene.util.cache import DEVICE_PAIRING_CODE_KEY, DEVICE_PAIRING_TOKEN_KEY

ONE_MINUTE = 60


@when('a device requests a pairing code')
def get_device_pairing_code(context):
    context.state = str(uuid.uuid4())
    response = context.client.get(
        '/v1/device/code?state={state}'.format(state=context.state))
    context.pairing_response = response


@when('the device is added to an account using the pairing code')
def add_device(context):
    """Imitate the logic in the account API to pair a device"""
    pairing_code_key = DEVICE_PAIRING_CODE_KEY.format(
        pairing_code=context.pairing_response.json['code']
    )
    pairing_data = context.cache.get(pairing_code_key)
    pairing_data = json.loads(pairing_data)
    pairing_data.update(uuid=context.device_id)
    context.cache.set_with_expiration(
            key=DEVICE_PAIRING_TOKEN_KEY.format(
                pairing_token=pairing_data['token']
            ),
            value=json.dumps(pairing_data),
            expiration=ONE_MINUTE
        )
    context.cache.delete(pairing_code_key)


@when('the device is activated')
def activate_device(context):
    activation_request = dict(
        token=context.pairing_response.json['token'],
        state=context.pairing_response.json['state'],
        platform='picroft',
        coreVersion='18.8.0',
        enclosureVersion='1.4.0'
    )
    response = context.client.post(
        '/v1/device/activate',
        data=json.dumps(activation_request),
        content_type='application/json'
    )
    context.activation_response = response


@then('the pairing code request is successful')
def check_pairing_code_response(context):
    response = context.pairing_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    assert_that(response.json, has_key('code'))
    assert_that(response.json, has_key('token'))
    assert_that(response.json['expiration'], equal_to(86400))
    assert_that(response.json['state'], equal_to(context.state))


@then('the device activation request is successful')
def validate_activation_response(context):
    response = context.activation_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    assert_that(response.json['uuid'], equal_to(context.device_id))
    assert_that(response.json, has_key('accessToken'))
    assert_that(response.json, has_key('refreshToken'))
    assert_that(response.json['expiration'], equal_to(86400))
