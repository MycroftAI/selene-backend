UPDATE
    account.refresh_token
SET
    refresh_token = %(new_refresh_token)s
WHERE
    account_id = %(account_id)s AND
    refresh_token = %(old_refresh_token)s
