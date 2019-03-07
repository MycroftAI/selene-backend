import json
import uuid
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key


@when('try to fetch device\'s setting')
def get_device_settings(context):
    device_id = context.device_login['uuid']
    context.response_setting = context.client.get('/device/{uuid}/setting'.format(uuid=device_id))


@then('a valid setting should be returned')
def validate_response_setting(context):
    response = context.response_setting
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    setting = json.loads(response.data)
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    assert_that(setting, has_key('uuid'))
    assert_that(setting, has_key('systemUnit'))
    assert_that(setting, has_key('timeFormat'))
    assert_that(setting, has_key('dateFormat'))
    assert_that(setting, has_key('ttsSettings'))


@when('the settings endpoint is a called to a nonexistent device')
def get_device_settings(context):
    context.get_invalid_setting_response = context.client.get('/device/{uuid}/setting'.format(uuid=str(uuid.uuid4())))


@then('a 204 status code should be returned for the setting')
def validate_response(context):
    response = context.get_invalid_setting_response
    assert_that(response.status_code, equal_to(HTTPStatus.NO_CONTENT))
