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
        INNER JOIN
            account.agreement ag ON ag.id = aa.agreement_id
        INNER JOIN
            account.account acc ON aa.account_id = acc.id
        INNER JOIN
            device.device dev ON acc.id = dev.account_id
        WHERE
            dev.id = %(device_id)s
    ),
    membership AS (
        SELECT
            json_build_object(
                'id', acc_mem.id,
                'type', mem.type,
                'start_date', lower(acc_mem.membership_ts_range)::DATE,
                'payment_method', acc_mem.payment_method,
                'payment_account_id', acc_mem.payment_account_id,
                'payment_id', acc_mem.payment_id
            )
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        INNER JOIN
            account.account acc ON acc_mem.account_id = acc.id
        INNER JOIN
            device.device dev ON acc.id = dev.account_id
        WHERE
            dev.id = %(device_id)s
            AND upper(acc_mem.membership_ts_range) IS NULL
    )
SELECT
    json_build_object(
        'id', acc.id,
        'email_address', acc.email_address,
        'username', acc.username,
        'last_activity', acc.last_activity_ts,
        'membership', (SELECT * FROM membership),
        'agreements', (SELECT * FROM agreements)
    ) as account
FROM
    account.account acc
INNER JOIN
    device.device dev ON acc.id = dev.account_id
WHERE
    dev.id = %(device_id)s
