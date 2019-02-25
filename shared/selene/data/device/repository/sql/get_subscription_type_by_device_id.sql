SELECT
    sub.rate_period
FROM
    device.device dev
INNER JOIN
    account.account acc ON dev.account_id = acc.id
LEFT JOIN
    account.account_subscription acc_sub ON acc.id = acc_sub.account_id
LEFT JOIN
    account.subscription sub ON acc_sub.subscription_id = sub.id
WHERE
    dev.id = %(device_id)s