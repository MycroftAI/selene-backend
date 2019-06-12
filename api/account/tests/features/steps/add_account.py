from binascii import b2a_base64
from datetime import date

from behave import given, then, when
from flask import json
from hamcrest import assert_that, equal_to, is_in, not_none

from selene.data.account import (
    AccountRepository,
    PRIVACY_POLICY,
    TERMS_OF_USE
)

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


@given('a user completes new account setup')
def build_new_account_request(context):
    context.new_account_request = new_account_request


@given('user does not specify an email address')
def remove_email_from_request(context):
    del(context.new_account_request['login']['email'])


@when('the new account request is submitted')
def call_add_account_endpoint(context):
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application/json'
    )


@then('the account will be added to the system')
def check_db_for_account(context):
    acct_repository = AccountRepository(context.db)
    account = acct_repository.get_account_by_email('bar@mycroft.ai')
    # add account to context so it will deleted by cleanup step
    context.accounts['bar'] = account
    assert_that(account, not_none())
    assert_that(
        account.email_address, equal_to('bar@mycroft.ai')
    )

    assert_that(len(account.agreements), equal_to(2))
    for agreement in account.agreements:
        assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
        assert_that(agreement.accept_date, equal_to(str(date.today())))
