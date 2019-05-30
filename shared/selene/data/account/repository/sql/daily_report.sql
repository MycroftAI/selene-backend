WITH
    account_count AS (
        SELECT
            COUNT (1)
        FROM
            account.account
        WHERE
            insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
    ),
    account_free_count AS (
        SELECT
            COUNT (1)
        FROM
            account.account acc
        LEFT JOIN
            account.account_membership acc_mem ON acc.id = acc_mem.account_id
        WHERE
            acc.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start)) AND acc_mem.account_id is NULL
    ),
    monthly_membership_count AS (
        SELECT
            COUNT (1)
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc_mem.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND mem.rate_period = 'month'
            AND UPPER (acc_mem.membership_ts_range) IS NULL
    ),
    monthly_membership_minus AS (
        SELECT
            COUNT (1)
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc_mem.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND mem.rate_period = 'month'
            AND UPPER (acc_mem.membership_ts_range) IS NOT NULL
    ),
    yearly_membership_count AS (
        SELECT
            COUNT (1)
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc_mem.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND mem.rate_period = 'yearly'
            AND UPPER (acc_mem.membership_ts_range) IS NULL
    ),
    yearly_membership_minus AS (
        SELECT
            COUNT (1)
        FROM
            account.account acc
        INNER JOIN
            account.account_membership acc_mem ON acc.id = acc_mem.account_id
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND mem.rate_period = 'yearly'
            AND UPPER (acc_mem.membership_ts_range) IS NOT NULL
    ),
    paid_membership_count AS (
        SELECT
            COUNT (1)
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc_mem.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND UPPER (acc_mem.membership_ts_range) IS NULL
    ),
    paid_memberhip_minus AS (
        SELECT
            COUNT (1)
        FROM
            account.account_membership acc_mem
        INNER JOIN
            account.membership mem ON acc_mem.membership_id = mem.id
        WHERE
            acc_mem.insert_ts::DATE > (CURRENT_DATE - INTERVAL %(start))
            AND UPPER (acc_mem.membership_ts_range) IS NULL
    )
SELECT
    json_build_object(
        'account_count', (SELECT * FROM account_count),
        'account_free_count', (SELECT * FROM account_free_count),
        'monthly_membership_count', (SELECT * FROM monthly_membership_count),
        'monthly_membership_minus', (SELECT * FROM monthly_membership_minus),
        'yearly_membership_count', (SELECT * FROM yearly_membership_count),
        'yearly_membership_minus', (SELECT * FROM yearly_membership_minus),
        'paid_membership_count', (SELECT * FROM paid_membership_count),
        'paid_membership_count', (SELECT * FROM paid_memberhip_minus)
    )