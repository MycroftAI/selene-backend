SELECT
    id,
    city_id
FROM
    device.account_defaults
WHERE
    city_id IN %(city_ids)s
