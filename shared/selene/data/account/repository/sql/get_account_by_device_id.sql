WITH
    refresh_tokens AS (
        SELECT
            array_agg(refresh_token)
        FROM
            account.refresh_token acc_ref
        INNER JOIN
            account.account acc ON acc_ref.account_id = acc.id
        INNER JOIN
            device.device dev ON acc.id = dev.account_id
        WHERE
            dev.id = %(device_id)s
    ),
    agreements AS (
        SELECT
            array_agg(
                json_build_object(
                    'id', aa.id,
                    'type', ag.agreement,
                    'accept_date', aa.accept_date
                )
            )
        FROM
            account.account_agreement aa
        INNER JOIN
            account.agreement ag ON ag.id = aa.agreement_id
        INNER JOIN
            account.account acc ON aa.account_id = acc.id
        INNER JOIN
            device.device dev ON acc.id = dev.account_id
        WHERE
            dev.id = %(device_id)s
    ),
    subscription AS (
        SELECT
            json_build_object(
                'id', asub.id,
                'type', s.subscription,
                'start_date', lower(asub.subscription_ts_range)::DATE,
                'stripe_customer_id', asub.stripe_customer_id
            )
        FROM
            account.account_subscription asub
        INNER JOIN
            account.subscription s ON asub.subscription_id = s.id
        INNER JOIN
            account.account acc ON asub.account_id = acc.id
        INNER JOIN
            device.device dev ON acc.id = dev.account_id
        WHERE
            dev.id = %(device_id)s
            AND upper(asub.subscription_ts_range) IS NULL
    )
SELECT
    json_build_object(
        'id', acc.id,
        'email_address', acc.email_address,
        'username', acc.username,
        'subscription', (SELECT * FROM subscription),
        'refresh_tokens', (SELECT * FROM refresh_tokens),
        'agreements', (SELECT * FROM agreements)
    ) as account
FROM
    account.account acc
INNER JOIN
    device.device dev ON acc.id = dev.account_id
WHERE
    dev.id = %(device_id)s

