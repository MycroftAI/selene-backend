SELECT
    id,
    country,
    state,
    city,
    time_zone,
    latitude,
    longitude
FROM
    device.geography
WHERE
    account_id = %(account_id)s
