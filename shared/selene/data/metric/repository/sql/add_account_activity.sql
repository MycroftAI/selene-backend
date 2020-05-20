INSERT INTO
    metric.account_activity (
        accounts,
        members,
        open_dataset
    )
VALUES
    (
        (SELECT count(*) FROM account.account),
        (
            SELECT
                count(*)
            FROM
                account.account_membership
            WHERE
                membership_ts_range @> current_date::timestamp
        ),
        (
            SELECT
                count(aa.*)
            FROM
                account.account_agreement aa
                INNER JOIN account.agreement a ON aa.agreement_id = a.id
            WHERE
                a.agreement = 'Open Dataset'
        )
    )
