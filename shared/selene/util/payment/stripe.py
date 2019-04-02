import os

import stripe


def create_stripe_account(token: str, email: str):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    customer = stripe.Customer.create(source=token, email=email)
    return customer.id


def create_stripe_subscription(customer_id, plan):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    request = stripe.Subscription.create(
        customer=customer_id,
        items=[{'plan': plan}]
    )

    return request.id


def cancel_stripe_subscription(subscription_id):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    active_stripe_subscription = stripe.Subscription.retrieve(subscription_id)
    active_stripe_subscription.delete()
