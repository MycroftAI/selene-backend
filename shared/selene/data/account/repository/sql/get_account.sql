WITH
    refresh_tokens AS (
        SELECT
            array_agg(refresh_token)
        FROM
            account.refresh_token
        WHERE
            account_id = {account_id_resolver}
    ),
    agreements AS (
        SELECT
            array_agg(
                json_build_object(
                    'name', ag.agreement,
                    'accepted_date', aa.accept_date
                )
            )
        FROM
            account.account_agreement aa
            INNER JOIN account.agreement ag ON ag.id = aa.agreement_id
        WHERE
            aa.account_id = {account_id_resolver}
    ),
    subscription AS (
        SELECT
            json_build_object(
                'type', s.subscription,
                'start_date', lower(asub.subscription_ts_range)::DATE
            )
        FROM
            account.account_subscription asub
            INNER JOIN account.subscription s ON asub.subscription_id = s.id
        WHERE
            asub.account_id = {account_id_resolver}
            AND upper(asub.subscription_ts_range) IS NULL
    )
SELECT
    json_build_object(
        'id', id,
        'email_address', email_address,
        'username', username,
        'subscription', (SELECT * FROM subscription),
        'refresh_tokens', (SELECT * FROM refresh_tokens),
        'agreements', (SELECT * FROM agreements)
    ) as account
FROM
    account.account
WHERE
    id = {account_id_resolver}

