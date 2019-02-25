SELECT
    acc.email_address
FROM
    account.account acc
INNER JOIN
    device.device dev ON acc.id = dev.account_id
WHERE
    dev.id = %(device_id)s