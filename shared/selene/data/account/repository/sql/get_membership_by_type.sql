SELECT
    id,
    type,
    rate,
    rate_period,
    stripe_plan
FROM
    account.membership
WHERE
    type = %(type)s