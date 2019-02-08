INSERT INTO
    account.account_subscription (
        account_id,
        subscription_id,
        subscription_ts_range,
        stripe_customer_id
    )
VALUES
    (
        %(account_id)s,
        (
            SELECT
                id
            FROM
                account.subscription
            WHERE
                subscription = %(subscription_type)s
        ),
        '[now,]',
        %(stripe_customer_id)s
    )
