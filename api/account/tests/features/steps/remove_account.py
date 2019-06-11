import os

import stripe
from behave import then, when
from hamcrest import assert_that, equal_to, not_none
from stripe.error import InvalidRequestError


@when('the user\'s account is deleted')
def account_deleted(context):
    context.response = context.client.delete('/api/account')


@then('the membership is removed from stripe')
def check_stripe(context):
    stripe_id = context.account.membership.payment_account_id
    assert_that(stripe_id, not_none())
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    subscription_not_found = False
    try:
        stripe.Subscription.retrieve(stripe_id)
    except InvalidRequestError:
        subscription_not_found = True
    assert_that(subscription_not_found, equal_to(True))
