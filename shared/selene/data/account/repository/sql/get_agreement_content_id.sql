SELECT
    content_id
FROM
    account.agreement
WHERE
    agreement = %(agreement_type)s
    AND version = %(version)s
