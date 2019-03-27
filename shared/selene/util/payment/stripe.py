from stripe import Customer, Subscription


def create_stripe_account(token: str, email: str):
    customer = Customer.create(source=token, email=email)
    return customer.id


def create_stripe_subscription(customer_id, plan):
    request = Subscription.create(
        customer=customer_id,
        items=[{'plan': plan}]
    )

    return request.id


def cancel_stripe_subscription(subscription_id):
    active_stripe_subscription = Subscription.retrieve(subscription_id)
    active_stripe_subscription.delete()
