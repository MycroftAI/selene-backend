UPDATE
    account.agreement
SET
    effective = %(date_range)s
WHERE
    agreement = %(agreement_type)s
    AND upper(effective) IS NULL
