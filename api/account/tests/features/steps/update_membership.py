import json
from datetime import date

from behave import given, when, then
from hamcrest import assert_that, equal_to, starts_with, none

from selene.api.testing import generate_access_token, generate_refresh_token
from selene.data.account import AccountRepository, Account, AccountAgreement, PRIVACY_POLICY
from selene.util.db import get_db_connection

new_account_request = dict(
    username='test',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedEmail=None,
        userEnteredEmail='test@mycroft.ai',
        password='12345678'
    ),
    support=dict(
        openDataset=True,
        membership='Maybe Later',
        paymentMethod=None,
        paymentAccountId=None
    )
)

free_membership = {
    'support': None
}

monthly_membership = {
    'membership': 'Monthly Membership',
    'paymentMethod': 'Stripe',
    'paymentToken': 'tok_visa'
}

yearly_membership = {
    'membership': 'Yearly Membership',
    'payment_method': 'Stripe',
    'payment_token': 'tok_visa'
}


@given('a user with a free account')
def create_account(context):
    context.account = Account(
        email_address='test@mycroft.ai',
        username='test',
        refresh_tokens=[],
        membership=None,
        agreements=[
            AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today())
        ]
    )
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        account_id = acct_repository.add(context.account, 'foo')
        context.account.id = account_id
        generate_access_token(context)
        generate_refresh_token(context)


@when('a monthly membership is added')
def update_membership(context):
    context.client.patch(
        '/api/account',
        data=json.dumps({'support': monthly_membership}),
        content_type='application_json'
    )


@when('the account is requested')
def request_account(context):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        context.response_account = AccountRepository(db).get_account_by_email('test@mycroft.ai')


@then('the account should have a monthly membership')
def monthly_account(context):
    account = context.response_account
    assert_that(account.membership.type, equal_to(monthly_membership['membership']))
    assert_that(account.membership.payment_account_id, starts_with('cus'))


@given('a user with a monthly membership')
def create_monthly_account(context):
    new_account_request['support'].update(
        membership=monthly_membership['membership'],
        paymentMethod=monthly_membership['paymentMethod'],
        paymentToken=monthly_membership['paymentToken']
    )
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
        data=json.dumps({'support': {'membership': yearly_membership['membership']}}),
        content_type='application_json'
    )


@then('the account should have a yearly membership')
def yearly_account(context):
    account = context.response_account
    assert_that(account.membership.type, equal_to(yearly_membership['membership']))
    assert_that(account.membership.payment_account_id, starts_with('cus'))
