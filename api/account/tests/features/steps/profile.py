import json
from datetime import date

from behave import given, then, when
from hamcrest import assert_that, equal_to, has_item, none, starts_with

from selene.data.account import AccountRepository, PRIVACY_POLICY
from selene.testing.api import (
    generate_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie
)
from selene.testing.membership import MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP

BAR_EMAIL_ADDRESS = 'bar@mycroft.ai'
STRIPE_METHOD = 'Stripe'
VISA_TOKEN = 'tok_visa'


@given('an account with a monthly membership')
def add_membership_to_account(context):
    """Use the API to add a monthly membership on Stripe

    The API is used so that the Stripe API can be interacted with.
    """
    context.username = 'foo'
    context.access_token = generate_access_token(context)
    set_access_token_cookie(context)
    context.refresh_token = generate_refresh_token(context)
    set_refresh_token_cookie(context)
    add_membership_via_api(context)


@given('an account without a membership')
def get_account_no_membership(context):
    context.username = 'foo'


@when('a user requests their profile')
def call_account_endpoint(context):
    context.response = context.client.get(
        '/api/account',
        content_type='application/json'
    )


@when('a monthly membership is added')
def add_monthly_membership(context):
    context.response = add_membership_via_api(context)


@when('the membership is cancelled')
def cancel_membership(context):
    membership_data = dict(
        newMembership=False,
        membershipType=None
    )
    context.response = context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application/json'
    )


def add_membership_via_api(context):
    membership_data = dict(
        newMembership=True,
        membershipType=MONTHLY_MEMBERSHIP,
        paymentMethod=STRIPE_METHOD,
        paymentToken=VISA_TOKEN
    )
    return context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application/json'
    )


@when('the membership is changed to yearly')
def change_to_yearly_account(context):
    membership_data = dict(
        newMembership=False,
        membershipType=YEARLY_MEMBERSHIP
    )
    context.response = context.client.patch(
        '/api/account',
        data=json.dumps(dict(membership=membership_data)),
        content_type='application/json'
    )


@then('user profile is returned')
def validate_response(context):
    response_data = context.response.json
    account = context.accounts['foo']
    assert_that(
        response_data['emailAddress'],
        equal_to(account.email_address)
    )
    assert_that(
        response_data['membership']['type'],
        equal_to('Monthly Membership')
    )
    assert_that(response_data['membership']['duration'], none())
    assert_that(
        response_data['membership'], has_item('id')
    )

    assert_that(len(response_data['agreements']), equal_to(2))
    agreement = response_data['agreements'][0]
    assert_that(agreement['type'], equal_to(PRIVACY_POLICY))
    assert_that(
        agreement['acceptDate'],
        equal_to(str(date.today().strftime('%B %d, %Y')))
    )
    assert_that(agreement, has_item('id'))


@then('the account should have a monthly membership')
def validate_monthly_account(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts['foo'].id
    )
    assert_that(
        membership.type,
        equal_to(MONTHLY_MEMBERSHIP)
    )
    assert_that(membership.payment_account_id, starts_with('cus'))
    assert_that(membership.start_date, equal_to(date.today()))
    assert_that(membership.end_date, none())


@then('the account should have no membership')
def validate_absence_of_membership(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts['foo'].id
    )
    assert_that(membership, none())


@then('the account should have a yearly membership')
def yearly_account(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts['foo'].id
    )
    assert_that(membership.type, equal_to(YEARLY_MEMBERSHIP))
    assert_that(membership.payment_account_id, starts_with('cus'))
