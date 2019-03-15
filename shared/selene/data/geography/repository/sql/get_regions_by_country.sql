SELECT
    id,
    region_code,
    name
FROM
    geography.region
WHERE
    country_id = %(country_id)s
