SELECT
    acc_mem.id,
    mem.type,
    LOWER(acc_mem.membership_ts_range) start_date,
    acc_mem.payment_method,
    payment_account_id
FROM
    account.account_membership acc_mem
INNER JOIN
    account.membership mem ON acc_mem.membership_id = mem.id
WHERE
    account_id = %(account_id)s AND UPPER(acc_mem.membership_ts_range) IS NULL