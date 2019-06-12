from binascii import b2a_base64
from datetime import date, datetime
from dataclasses import dataclass
from unittest.mock import call, patch

from behave import given, then, when
from flask import json
from hamcrest import assert_that, equal_to, is_in, none, not_none

from selene.data.account import (
    AccountRepository,
    MONTHLY_MEMBERSHIP,
    PRIVACY_POLICY,
    TERMS_OF_USE
)
from selene.testing.account import add_account

new_account_request = dict(
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedPlatform=None,
        federatedToken=None,
        email=b2a_base64(b'bar@mycroft.ai').decode(),
        password=b2a_base64(b'bar').decode()
    )
)


@dataclass
class StripeMock(object):
    """Object intended to behave like stripe Customer/Subscription create"""
    id: str


@given('a user completes new account setup')
def build_new_account_request(context):
    context.new_account_request = new_account_request


@given('user opts out of membership')
def add_maybe_later_membership(context):
    context.new_account_request['support'].update(
        membership=None,
        paymentMethod=None,
        paymentAccountId=None
    )


@given('user opts into a membership')
def change_membership_option(context):
    context.new_account_request['support'].update(
        membership='Monthly Membership',
        paymentMethod='Stripe',
        paymentToken='tok_visa'
    )


@given('user does not specify an email address')
def remove_email_from_request(context):
    del(context.new_account_request['login']['email'])


@given('a new account without a membership')
def add_account_no_membership(context):
    new_account_overrides = dict(
        email_address='bar@mycroft.ai',
        username='bar',
        membership=None
    )
    context.bar_account = add_account(context.db, **new_account_overrides)


@when('the new account request is submitted')
def call_add_account_endpoint(context):
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application/json'
    )


@when('a user opts into a membership during on-boarding')
def call_update_account_endpoint(context):
    onboarding_request = dict(
        membership=dict(
            newMembership=True,
            membershipType=MONTHLY_MEMBERSHIP,
            paymentToken='test_payment_token',
            paymentMethod='Stripe'
        )
    )
    with patch('stripe.Subscription.create') as subscription_patch:
        subscription_patch.return_value = StripeMock(id='test_subscription')
        with patch('stripe.Customer.create') as customer_patch:
            customer_patch.return_value = StripeMock(id='test_customer')
            context.response = context.client.patch(
                '/api/account',
                data=json.dumps(onboarding_request),
                content_type='application/json'
            )
            assert_that(
                customer_patch.mock_calls,
                equal_to([call(
                    email='bar@mycroft.ai',
                    source='test_payment_token'
                )])
            )
        assert_that(
            subscription_patch.mock_calls,
            equal_to([call(
                customer='test_customer',
                items=[{'plan': 'monthly_premium'}])
            ]))


@then('the account will be added to the system')
def check_db_for_account(context):
    acct_repository = AccountRepository(context.db)
    account = acct_repository.get_account_by_email('bar@mycroft.ai')
    assert_that(account, not_none())
    assert_that(
        account.email_address, equal_to('bar@mycroft.ai')
    )

    assert_that(len(account.agreements), equal_to(2))
    for agreement in account.agreements:
        assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
        assert_that(agreement.accept_date, equal_to(str(date.today())))


@then('the account will be updated with the membership')
def validate_membership_update(context):
    account_repository = AccountRepository(context.db)
    membership = account_repository.get_active_account_membership(
        context.account.id
    )
    assert_that(membership.type, equal_to(MONTHLY_MEMBERSHIP))
    assert_that(membership.start_date, equal_to(datetime.utcnow().date()))
    assert_that(membership.end_date, none())
