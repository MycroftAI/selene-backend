SELECT
    id,
    name,
    gmt_offset,
    dst_offset
FROM
    geography.timezone
WHERE
    country_id = %(country_id)s
