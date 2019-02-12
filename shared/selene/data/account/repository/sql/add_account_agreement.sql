INSERT INTO
    account.account_agreement (account_id, agreement_id, accept_date)
VALUES
    (
        %(account_id)s,
        (
            SELECT
                id
            FROM
                account.agreement
            WHERE
                agreement = %(agreement_name)s
        ),
        '[now,]'
    )
