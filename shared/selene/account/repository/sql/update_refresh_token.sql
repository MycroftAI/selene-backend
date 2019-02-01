UPDATE
    account.account
SET
    refresh_token = %(refresh_token)s
WHERE
    id = %(account_id)s
