SELECT
    id,
    city_id
FROM
    device.geography
WHERE
    city_id IN %(city_ids)s
