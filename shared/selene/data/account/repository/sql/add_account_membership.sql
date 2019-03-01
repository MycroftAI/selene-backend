INSERT INTO
    account.account_membership (
        account_id,
        membership_id,
        membership_ts_range,
        stripe_customer_id
    )
VALUES
    (
        %(account_id)s,
        (
            SELECT
                id
            FROM
                account.membership
            WHERE
                type = %(membership_type)s
        ),
        '[now,]',
        %(stripe_customer_id)s
    )
