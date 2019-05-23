import json

from behave import given, when, then
from hamcrest import assert_that, equal_to, has_key, none, not_none

from selene.data.device import DeviceRepository
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db


@given('a device pairing code')
def set_device_pairing_code(context):
    pairing_data = dict(
        code='ABC123',
        state='this is a state',
        token='this is a token',
        expiration=84600
    )
    cache = SeleneCache()
    cache.set_with_expiration(
        'pairing.code:ABC123',
        json.dumps(pairing_data),
        expiration=86400
    )
    context.pairing_data = pairing_data
    context.pairing_code = 'ABC123'


@when('an API request is sent to add a device')
def add_device(context):
    device = dict(
        city='Kansas City',
        country='United States',
        name='home',
        pairingCode=context.pairing_code,
        placement='kitchen',
        region='Missouri',
        timezone='America/Chicago',
        wakeWord='Hey Mycroft',
        voice='American Male'
    )
    response = context.client.post(
        '/api/devices',
        data=json.dumps(device),
        content_type='application_json'
    )
    context.response = response


@then('the pairing code is removed from cache')
def validate_pairing_code_removal(context):
    cache = SeleneCache()
    pairing_data = cache.get('pairing.code:ABC123')
    assert_that(pairing_data, none())


@then('the device is added to the database')
def validate_response(context):
    device_id = context.response.data.decode()
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    device_repository = DeviceRepository(db)
    device = device_repository.get_device_by_id(device_id)

    assert_that(device, not_none())
    assert_that(device.name, equal_to('home'))
    assert_that(device.placement, equal_to('kitchen'))
    assert_that(device.account_id, equal_to(context.account.id))


@then('the pairing token is added to cache')
def validate_pairing_token(context):
    device_id = context.response.data.decode()
    cache = SeleneCache()
    pairing_data = cache.get('pairing.token:this is a token')
    pairing_data = json.loads(pairing_data)

    assert_that(pairing_data['uuid'], equal_to(device_id))
    assert_that(pairing_data['state'], equal_to(context.pairing_data['state']))
    assert_that(pairing_data['token'], equal_to(context.pairing_data['token']))
