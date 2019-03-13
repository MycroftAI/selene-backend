SELECT
    *
FROM
    account.account_membership
WHERE
    account_id = %(account_id)s and membership_ts_range @> '[now,)'