import os

import stripe
from behave import then, when
from hamcrest import assert_that, equal_to
from stripe.error import InvalidRequestError

from selene.data.account import AccountRepository


@when('the user\'s account is deleted')
def account_deleted(context):
    acct_repository = AccountRepository(context.db)
    membership = acct_repository.get_active_account_membership(
        context.accounts['foo'].id
    )
    context.accounts['foo'].membership = membership
    context.response = context.client.delete('/api/account')


@then('the membership is removed from stripe')
def check_stripe(context):
    account = context.accounts['foo']
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    subscription_not_found = False
    try:
        stripe.Subscription.retrieve(account.membership.payment_account_id)
    except InvalidRequestError:
        subscription_not_found = True
    assert_that(subscription_not_found, equal_to(True))
