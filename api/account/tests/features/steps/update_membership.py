import json

from behave import given, when, then
from hamcrest import assert_that, equal_to, starts_with, none

from selene.api.testing import generate_access_token, generate_refresh_token
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection

new_account_request = dict(
    username='test',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedEmail=None,
        userEnteredEmail='test@mycroft.ai',
        password='test'
    ),
    support=dict(
        openDataset=True,
        membership=None
    )
)

free_membership = {
    'support': None
}

monthly_membership = {
    'support': {
        'membership': 'Monthly Membership',
        'payment_method': 'Stripe',
        'payment_token': 'tok_visa'
    }
}

yearly_membership = {
    'support': {
        'membership': 'Yearly Membership',
        'payment_method': 'Stripe',
        'payment_token': 'tok_visa'
    }
}


@given('a user with a free account')
def create_account_free_account(context):
    context.client.post(
        '/api/account',
        data=json.dumps(new_account_request),
        content_type='application_json'
    )
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        account = AccountRepository(db).get_account_by_email(new_account_request['login']['userEnteredEmail'])
        context.account = account
        generate_access_token(context)
        generate_refresh_token(context)


@when('a monthly membership is added')
def update_membership(context):
    context.client.patch(
        '/api/account',
        data=json.dumps(monthly_membership),
        content_type='application_json'
    )


@when('the account is requested')
def request_account(context):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        context.response_account = AccountRepository(db).get_account_by_email('test@mycroft.ai')


@then('the account should have a monthly membership')
def monthly_account(context):
    account = context.response_account
    assert_that(account.membership.type, equal_to(monthly_membership['support']['membership']))
    assert_that(account.membership.payment_account_id, starts_with('cus'))


@given('a user with a monthly membership')
def create_monthly_account(context):
    new_account_request['membership'] = monthly_membership
    context.client.post(
        '/api/account',
        data=json.dumps(new_account_request),
        content_type='application_json'
    )
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        account = AccountRepository(db).get_account_by_email(new_account_request['login']['userEnteredEmail'])
        context.account = account
        generate_access_token(context)
        generate_refresh_token(context)


@when('the membership is cancelled')
def cancel_membership(context):
    context.client.patch(
        '/api/account',
        data=json.dumps(free_membership),
        content_type='application_json'
    )


@then('the account should have no membership')
def free_account(context):
    account = context.response_account
    assert_that(account.membership, none())


@when('the membership is changed to yearly')
def change_to_yearly_account(context):
    context.client.patch(
        '/api/account',
        data=json.dumps(yearly_membership),
        content_type='application_json'
    )


@then('the account should have a yearly membership')
def yearly_account(context):
    account = context.response_account
    assert_that(account.membership.type, equal_to(yearly_membership['support']['membership']))
    assert_that(account.membership.payment_account_id, starts_with('cus'))
