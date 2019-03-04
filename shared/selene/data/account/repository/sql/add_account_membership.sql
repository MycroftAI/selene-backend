INSERT INTO
    account.account_membership (
        account_id,
        membership_id,
        membership_ts_range,
        payment_method,
        payment_account_id
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
        %(payment_method)s,
        %(payment_account_id)s
    )
