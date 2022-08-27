WITH
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
            INNER JOIN account.agreement ag ON ag.id = aa.agreement_id
        WHERE
            aa.account_id = {account_id_resolver}
    ),
    membership AS (
        SELECT
            json_build_object(
                'id', am.id,
                'type', m.type,
                'start_date', lower(am.membership_ts_range)::DATE,
                'payment_method', am.payment_method,
                'payment_account_id', am.payment_account_id,
                'payment_id', am.payment_id
            )
        FROM
            account.account_membership am
            INNER JOIN account.membership m ON am.membership_id = m.id
        WHERE
            am.account_id = {account_id_resolver}
            AND upper(am.membership_ts_range) IS NULL
    )
SELECT
    json_build_object(
        'id', id,
        'email_address', email_address,
        'federated_login', password is null,
        'username', username,
        'last_activity', last_activity_ts,
        'membership', (SELECT * FROM membership),
        'agreements', (SELECT * FROM agreements)
    ) as account
FROM
    account.account
WHERE
    id = {account_id_resolver}
