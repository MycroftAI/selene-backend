SELECT
    id,
    country,
    postal_code,
    time_zone
FROM
    device.location
WHERE
    account_id = %(account_id)s
