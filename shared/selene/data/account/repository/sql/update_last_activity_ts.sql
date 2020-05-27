UPDATE
    account.account
SET
    last_activity_ts = %(last_activity_ts)s
WHERE
    id = %(account_id)s
