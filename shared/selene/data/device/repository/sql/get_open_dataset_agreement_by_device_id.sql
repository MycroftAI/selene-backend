SELECT
    acc_agr.id
FROM
    device.device dev
INNER JOIN
    account.account acc ON dev.account_id = acc.id
INNER JOIN
    account.account_agreement acc_agr ON acc.id = acc_agr.account_id
INNER JOIN
    account.agreement agr ON acc_agr.agreement_id = agr.id
WHERE
    dev.id = %(device_id)s AND agr.agreement = 'Open Dataset'