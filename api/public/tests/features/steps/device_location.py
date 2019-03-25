import json
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, equal_to, has_key


@when('a api call to get the location is done')
def get_device_location(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_location_response = context.client.get(
        '/v1/device/{uuid}/location'.format(uuid=device_id),
        headers=headers
    )


@then('the location should be retrieved')
def validate_location(context):
    response = context.get_location_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    location = json.loads(response.data)
    assert_that(location, has_key('coordinate'))
    assert_that(location, has_key('timezone'))
    assert_that(location, has_key('city'))

    coordinate = location['coordinate']
    assert_that(coordinate, has_key('latitude'))
    assert_that(coordinate, has_key('longitude'))

    timezone = location['timezone']
    assert_that(timezone, has_key('name'))
    assert_that(timezone, has_key('offset'))
    assert_that(timezone, has_key('dstOffset'))

    city = location['city']
    assert_that(city, has_key('name'))
    assert_that(city, has_key('state'))

    state = city['state']
    assert_that(state, has_key('name'))
    assert_that(state, has_key('country'))

    country = state['country']
    assert_that(country, has_key('name'))
