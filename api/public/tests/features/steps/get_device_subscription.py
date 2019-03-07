import json
import uuid
from datetime import date
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, has_entry, equal_to

from selene.data.account import AccountRepository, AccountMembership
from selene.util.db import get_db_connection


@when('the subscription endpoint is called')
def get_device_subscription(context):
    device_id = context.device_login['uuid']
    context.subscription_response = context.client.get('/device/{uuid}/subscription'.format(uuid=device_id))


@then('free type should be returned')
def validate_response(context):
    response = context.subscription_response
    assert_that(response.status_code, HTTPStatus.OK)
    subscription = json.loads(response.data)
    assert_that(subscription, has_entry('@type', 'free'))


@when('the subscription endpoint is called for a monthly account')
def get_device_subscription(context):
    membership = AccountMembership(
        start_date=date.today(),
        type='Monthly Membership',
        payment_method='Stripe',
        payment_account_id='test_monthly'
    )
    device_id = context.device_login['uuid']
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        AccountRepository(db)._add_membership(context.account.id, membership)
    context.subscription_response = context.client.get('/device/{uuid}/subscription'.format(uuid=device_id))


@then('monthly type should be returned')
def validate_response_monthly(context):
    response = context.subscription_response
    assert_that(response.status_code, HTTPStatus.OK)
    subscription = json.loads(response.data)
    assert_that(subscription, has_entry('@type', 'Monthly Membership'))


@when('try to get the subscription for a nonexistent device')
def get_subscription_nonexistent_device(context):
    context.invalid_subscription_response = context.client.get('/device/{uuid}/subscription'.format(uuid=str(uuid.uuid4())))


@then('204 status code should be returned for the subscription endpoint')
def validate_nonexistent_device(context):
    response = context.invalid_subscription_response
    assert_that(response.status_code, equal_to(HTTPStatus.NO_CONTENT))
