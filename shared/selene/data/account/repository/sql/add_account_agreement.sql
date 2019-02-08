INSERT INTO
    account.account_agreement (account_id, agreement_id, agreement_ts_range)
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
