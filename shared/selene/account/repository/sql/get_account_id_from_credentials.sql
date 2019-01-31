SELECT
    a.id
FROM
    account.account a
INNER JOIN
    account.account_login al ON al.account_id = a.id
WHERE
    a.email_address = %(email_address)s AND
    al.token = crypt(%(password)s, al.token)
