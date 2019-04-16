import json
from datetime import date

from behave import given, when, then
from hamcrest import assert_that, equal_to, starts_with, none

from selene.api.testing import generate_access_token, generate_refresh_token
from selene.data.account import (
    AccountRepository,
    Account,
    AccountAgreement,
    PRIVACY_POLICY
)
from selene.util.db import get_db_connection

new_account_request = dict(
    username='test',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedPlatform=None,
        federatedToken=None,
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

MONTHLY_MEMBERSHIP = 'Monthly Membership'
STRIPE_METHOD = 'Stripe'
VISA_TOKEN = 'tok_visa'
YEARLY_MEMBERSHIP = 'Yearly Membership'


@given('a user with a free account')
def create_account(context):
    context.account = Account(
        email_address='test@mycroft.ai',
        username='test',
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
    membership_data = dict(
        newMembership=True,
        membershipType=MONTHLY_MEMBERSHIP,
        paymentMethod=STRIPE_METHOD,
        paymentToken=VISA_TOKEN
    )
    context.response = context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application_json'
    )


@when('the account is requested')
def request_account(context):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        context.response_account = AccountRepository(db).get_account_by_email(
            'test@mycroft.ai'
        )


@then('the account should have a monthly membership')
def monthly_account(context):
    account = context.response_account
    assert_that(
        account.membership.type,
        equal_to(MONTHLY_MEMBERSHIP)
    )
    assert_that(account.membership.payment_account_id, starts_with('cus'))


@given('a user with a monthly membership')
def create_monthly_account(context):
    new_account_request['support'].update(
        membership=MONTHLY_MEMBERSHIP,
        paymentMethod=STRIPE_METHOD,
        paymentToken=VISA_TOKEN
    )
    context.client.post(
        '/api/account',
        data=json.dumps(new_account_request),
        content_type='application_json'
    )
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        account_repository = AccountRepository(db)
        account = account_repository.get_account_by_email(
            new_account_request['login']['userEnteredEmail']
        )
        context.account = account
        generate_access_token(context)
        generate_refresh_token(context)


@when('the membership is cancelled')
def cancel_membership(context):
    membership_data = dict(
        newMembership=False,
        membershipType=None
    )
    context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application_json'
    )


@then('the account should have no membership')
def free_account(context):
    account = context.response_account
    assert_that(account.membership, none())


@when('the membership is changed to yearly')
def change_to_yearly_account(context):
    membership_data = dict(
        newMembership=False,
        membershipType=YEARLY_MEMBERSHIP
    )
    context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application_json'
    )


@then('the account should have a yearly membership')
def yearly_account(context):
    account = context.response_account
    assert_that(account.membership.type, equal_to(YEARLY_MEMBERSHIP))
    assert_that(account.membership.payment_account_id, starts_with('cus'))
