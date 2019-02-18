from datetime import date
from http import HTTPStatus

from behave import then, when
from flask import json
from hamcrest import assert_that, equal_to, is_in, not_none

from selene.data.account import AccountRepository, PRIVACY_POLICY, TERMS_OF_USE
from selene.util.db import get_db_connection

new_account_request = dict(
    displayName='barfoo',
    termsOfUse=True,
    privacyPolicy=True,
    login=dict(
        federatedEmail=None,
        userEnteredEmail='bar@mycroft.ai',
        password='bar'
    ),
    support=dict(
        openDataset=True,
        membership='Monthly Supporter',
        stripeCustomerId='barstripe'
    )
)


@when('a valid new account request is submitted')
def call_add_account_endpoint(context):
    context.new_account_request = new_account_request
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application_json'
    )


@when('a request is sent without an email address')
def create_account_without_email(context):
    context.new_account_request = new_account_request
    login_data = context.new_account_request['login']
    del(login_data['userEnteredEmail'])
    context.new_account_request['login'] = login_data
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        '/api/account',
        data=json.dumps(context.new_account_request),
        content_type='application_json'
    )


@then('the request will be successful')
def check_request_success(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))


@then('the account will be added to the system')
def check_db_for_account(context):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        acct_repository = AccountRepository(db)
        account = acct_repository.get_account_by_email('bar@mycroft.ai')
        assert_that(account, not_none())
        assert_that(
            account.email_address, equal_to('bar@mycroft.ai')
        )
        assert_that(account.display_name, equal_to('barfoo'))
        assert_that(account.subscription.type, equal_to('Monthly Supporter'))
        assert_that(
            account.subscription.stripe_customer_id,
            equal_to('barstripe')
        )
        assert_that(len(account.agreements), equal_to(2))
        for agreement in account.agreements:
            assert_that(agreement.type, is_in((PRIVACY_POLICY, TERMS_OF_USE)))
            assert_that(agreement.accept_date, equal_to(str(date.today())))


@then('the request will fail with a bad request error')
def check_for_bad_request(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.BAD_REQUEST))
