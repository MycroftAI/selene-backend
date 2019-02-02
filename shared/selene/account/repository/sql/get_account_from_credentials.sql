SELECT
    a.id,
    a.email_address,
    array_agg(rt.refresh_token) as refresh_tokens
FROM
    account.account a
INNER JOIN
    account.account_login al ON al.account_id = a.id
LEFT JOIN
    account.refresh_token rt ON rt.account_id = a.id
WHERE
    a.email_address = %(email_address)s AND
    al.token = crypt(%(password)s, al.token)
GROUP BY
    a.id,
    a.email_address
