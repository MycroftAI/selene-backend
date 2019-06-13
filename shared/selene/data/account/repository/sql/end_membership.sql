UPDATE
    account.account_membership
SET
    membership_ts_range = %(membership_ts_range)s
WHERE
    id = %(id)s