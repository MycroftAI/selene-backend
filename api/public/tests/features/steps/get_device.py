import json
import uuid
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key


@when('device is retrieved')
def get_device(context):
    context.get_device_response = context.client.get('/device/{uuid}'.format(uuid=context.device_id))


@then('a valid device should be returned')
def validate_response(context):
    response = context.get_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    device = json.loads(response.data)
    assert_that(device, has_key('name'))
    assert_that(device, has_key('description'))
    assert_that(device, has_key('coreVersion'))
    assert_that(device, has_key('enclosureVersion'))
    assert_that(device, has_key('platform'))


@when('try to fetch a device that doesn\'t exist in the database')
def get_invalid_device(context):
    context.get_invalid_device_response = context.client.get('/device/{uuid}'.format(uuid=str(uuid.uuid4())))


@then('a 204 status code should be returned')
def validate_invalid_response(context):
    response = context.get_invalid_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.NO_CONTENT))
