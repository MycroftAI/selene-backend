DELETE FROM
    account.account_agreement
WHERE
    account_id = %(account_id)s
    AND agreement_id in (SELECT id FROM account.agreement WHERE agreement = %(agreement_type)s)
