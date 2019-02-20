import json
import uuid

from behave import given, when, then
from hamcrest import assert_that, equal_to, has_key


@given('a device pairing code')
def get_device_pairing_code(context):
    state = str(uuid.uuid4())
    response = context.client.get('/device/code?state={state}'.format(state=state))
    context.pairing = json.loads(response.data)
    context.state = state


@when('a device is added to an account using the pairing code')
def add_device(context):
    device = {
        'name': 'home',
        'wake_word_id': context.wake_word_id,
        'text_to_speech_id': context.text_to_speech_id
    }
    response = context.client.post('/api/account/{account_id}/device?code={code}'
                                   .format(account_id=context.account.id, code=context.pairing['code']),
                                   data=json.dumps(device),
                                   content_type='application_json')
    context.device_id = response.data.decode('utf-8')


@when('device is activated')
def activate_device(context):
    activate = {
        'token': context.pairing['token'],
        'state': context.pairing['state'],
        'platform': 'picroft',
        'core_version': '18.8.0',
        'enclosure_version': '1.4.0'
    }
    response = context.client.post('/device/activate', data=json.dumps(activate), content_type='application_json')
    context.activate_device_response = response


@then('a login session should be returned')
def validate_response(context):
    assert_that(context.pairing['state'], equal_to(context.state))
    login = json.loads(context.activate_device_response.data)
    assert_that(has_key(equal_to('uuid')))
    assert_that(has_key(equal_to('accessToken')))
    assert_that(has_key(equal_to('refreshToken')))
    assert_that(has_key(equal_to('expiration')))
    assert_that(context.device_id, equal_to(login['uuid']))
