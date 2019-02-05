SELECT
    a.id,
    a.email_address,
    a.password,
    array_agg(rt.refresh_token) as refresh_tokens
FROM
    account.account a
LEFT JOIN
    account.refresh_token rt ON rt.account_id = a.id
WHERE
    a.email_address = %(email_address)s AND
    a.password = %(password)s
GROUP BY
    a.id,
    a.email_address,
    a.password
