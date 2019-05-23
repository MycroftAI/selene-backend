import json
import uuid
from http import HTTPStatus

from behave import when, then, given
from hamcrest import assert_that, equal_to, has_key, not_none, is_not

from selene.api.etag import ETagManager, device_etag_key

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
        '/v1/device/{uuid}'.format(uuid=device_id),
        headers=headers
    )
    context.device_etag = context.get_device_response.headers.get('ETag')


@then('a valid device should be returned')
def validate_response(context):
    response = context.get_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    device = json.loads(response.data)
    assert_that(device, has_key('uuid'))
    assert_that(device, has_key('name'))
    assert_that(device, has_key('description'))
    assert_that(device, has_key('coreVersion'))
    assert_that(device, has_key('enclosureVersion'))
    assert_that(device, has_key('platform'))
    assert_that(device, has_key('user'))
    assert_that(device['user'], has_key('uuid'))
    assert_that(device['user']['uuid'], equal_to(context.account.id))


@when('try to fetch a device without the authorization header')
def get_invalid_device(context):
    context.get_invalid_device_response = context.client.get('/v1/device/{uuid}'.format(uuid=str(uuid.uuid4())))


@when('try to fetch a not allowed device')
def get_not_allowed_device(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_invalid_device_response = context.client.get(
        '/v1/device/{uuid}'.format(uuid=str(uuid.uuid4())),
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
        '/v1/device/{uuid}'.format(uuid=device_id),
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


@given('a device with a valid etag')
def get_device_etag(context):
    etag_manager: ETagManager = context.etag_manager
    device_id = context.device_login['uuid']
    context.device_etag = etag_manager.get(device_etag_key(device_id))


@when('try to fetch a device using a valid etag')
def get_device_using_etag(context):
    etag = context.device_etag
    assert_that(etag, not_none())
    access_token = context.device_login['accessToken']
    device_uuid = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.response_using_etag = context.client.get(
        '/v1/device/{uuid}'.format(uuid=device_uuid),
        headers=headers
    )


@then('304 status code should be returned by the device endpoint')
def validate_etag(context):
    response = context.response_using_etag
    assert_that(response.status_code, equal_to(HTTPStatus.NOT_MODIFIED))


@given('a device\'s etag expired by the web ui')
def expire_etag(context):
    etag_manager: ETagManager = context.etag_manager
    device_id = context.device_login['uuid']
    context.device_etag = etag_manager.get(device_etag_key(device_id))
    etag_manager.expire_device_etag_by_device_id(device_id)


@when('try to fetch a device using an expired etag')
def fetch_device_expired_etag(context):
    etag = context.device_etag
    assert_that(etag, not_none())
    access_token = context.device_login['accessToken']
    device_uuid = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.response_using_invalid_etag = context.client.get(
        '/v1/device/{uuid}'.format(uuid=device_uuid),
        headers=headers
    )


@then('should return status 200')
def validate_status_code(context):
    response = context.response_using_invalid_etag
    assert_that(response.status_code, equal_to(HTTPStatus.OK))


@then('a new etag')
def validate_new_etag(context):
    etag = context.device_etag
    response = context.response_using_invalid_etag
    etag_from_response = response.headers.get('ETag')
    assert_that(etag, is_not(etag_from_response))
