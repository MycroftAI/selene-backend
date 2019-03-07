import json
import uuid
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key

new_fields = dict(
    platform='mycroft_mark_1',
    coreVersion='19.2.0',
    enclosureVersion='1.4.0'
)


@when('device is retrieved')
def get_device(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    device_id = context.device_login['uuid']
    context.get_device_response = context.client.get(
        '/device/{uuid}'.format(uuid=device_id),
        headers=headers
    )


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


@when('try to fetch a device without the authorization header')
def get_invalid_device(context):
    context.get_invalid_device_response = context.client.get('/device/{uuid}'.format(uuid=str(uuid.uuid4())))


@when('try to fetch a not allowed device')
def get_not_allowed_device(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_invalid_device_response = context.client.get(
        '/device/{uuid}'.format(uuid=str(uuid.uuid4())),
        headers=headers
    )


@then('a 401 status code should be returned')
def validate_invalid_response(context):
    response = context.get_invalid_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))


@when('the device is updated')
def update_device(context):
    login = context.device_login
    access_token = login['accessToken']
    device_id = login['uuid']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))

    context.update_device_response = context.client.patch(
        '/device/{uuid}'.format(uuid=device_id),
        data=json.dumps(new_fields),
        content_type='application_json',
        headers=headers
    )


@then('the information should be updated')
def validate_update(context):
    response = context.update_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))

    response = context.get_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    device = json.loads(response.data)
    assert_that(device, has_key('name'))
    assert_that(device['coreVersion'], equal_to(new_fields['coreVersion']))
    assert_that(device['enclosureVersion'], equal_to(new_fields['enclosureVersion']))
    assert_that(device['platform'], equal_to(new_fields['platform']))
