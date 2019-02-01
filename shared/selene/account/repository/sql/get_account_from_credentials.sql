SELECT
    a.id,
    a.email_address,
    a.refresh_token
FROM
    account.account a
INNER JOIN
    account.account_login al ON al.account_id = a.id
WHERE
    a.email_address = %(email_address)s AND
    al.token = crypt(%(password)s, al.token)
