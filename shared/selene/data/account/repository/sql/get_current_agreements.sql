SELECT
    id,
    agreement,
    version,
    content_id,
    lower(effective) as effective_date
FROM
    account.agreement
WHERE
    effective @> CURRENT_DATE
