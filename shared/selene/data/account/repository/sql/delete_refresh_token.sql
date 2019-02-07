DELETE FROM
    account.refresh_token
WHERE
    account_id = %(account_id)s AND
    refresh_token = %(refresh_token)s
