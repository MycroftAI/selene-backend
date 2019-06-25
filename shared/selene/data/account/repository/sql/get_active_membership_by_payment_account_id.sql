SELECT
    acc_mem.id,
    mem.type,
    LOWER(acc_mem.membership_ts_range)::date start_date,
    acc_mem.payment_method,
    payment_account_id,
    payment_id
FROM
    account.account_membership acc_mem
INNER JOIN
    account.membership mem ON acc_mem.membership_id = mem.id
WHERE
    acc_mem.payment_account_id = %(payment_account_id)s AND UPPER(acc_mem.membership_ts_range) IS NULL
