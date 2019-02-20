from datetime import date

from behave import given, then, when
from flask import json
from hamcrest import assert_that, equal_to, is_in, none, not_none

from selene.data.account import AccountRepository, PRIVACY_POLICY, TERMS_OF_USE
from selene.util.db import get_db_connection

new_account_request = dict(
    username='barfoo',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedEmail=None,
        userEnteredEmail='bar@mycroft.ai',
        password='bar'
    ),
    support=dict(openDataset=True)
)


@given('a user completes on-boarding')
def build_new_account_request(context):
    context.new_account_request = new_account_request


@given('user opts out of membership')
def add_maybe_later_membership(context):
    context.new_account_request['support'].update(
        membership='Maybe Later',
        stripeCustomerId=None
    )


@given('user opts into a membership')
def change_membership_option(context):
    context.new_account_request['support'].update(
        membership='Monthly Supporter',
        stripeCustomerId='barstripe'
    )


@given('user does not specify an email address')
def remove_email_from_request(context):
    del(context.new_account_request['login']['userEnteredEmail'])


@when('the new account request is submitted')
def call_add_account_endpoint(context):
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application_json'
    )


@then('the account will be added to the system {membership_option}')
def check_db_for_account(context, membership_option):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        account = acct_repository.get_account_by_email('bar@mycroft.ai')
        assert_that(account, not_none())
        assert_that(
            account.email_address, equal_to('bar@mycroft.ai')
        )
        assert_that(account.username, equal_to('barfoo'))
        if membership_option == 'with a membership':
            assert_that(account.subscription.type, equal_to('Monthly Supporter'))
            assert_that(
                account.subscription.stripe_customer_id,
                equal_to('barstripe')
            )
        elif membership_option == 'without a membership':
            assert_that(account.subscription, none())

        assert_that(len(account.agreements), equal_to(2))
        for agreement in account.agreements:
            assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
            assert_that(agreement.accept_date, equal_to(str(date.today())))
