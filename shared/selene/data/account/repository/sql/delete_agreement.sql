DELETE FROM
    account.agreement
WHERE
    agreement = %(agreement_type)s
    AND version = %(version)s
