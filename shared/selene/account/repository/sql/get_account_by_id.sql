SELECT
    id,
    email_address,
    refresh_token
FROM
    account.account
WHERE
    id = %(account_id)s
