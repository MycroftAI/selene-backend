SELECT
    a.id,
    a.email_address,
    a.password,
    array_agg(rt.refresh_token) as refresh_tokens
FROM
    account.account a
LEFT JOIN
    account.refresh_token rt on a.id = rt.account_id
WHERE
    a.email_address = %(email_address)s
GROUP BY
    a.id,
    a.email_address,
    a.password
