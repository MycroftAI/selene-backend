DELETE FROM
    account.refresh_token
WHERE
    account_id = %(account_id) AND
    refresh_token = %(refresh_token)s
