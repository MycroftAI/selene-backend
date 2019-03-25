SELECT
    g.id,
    cntry.name AS country,
    r.name as region,
    cty.name AS city,
    t.name as time_zone,
    latitude,
    longitude
FROM
    device.geography g
    INNER JOIN geography.city cty ON g.city_id = cty.id
    INNER JOIN geography.country cntry ON g.country_id = cntry.id
    INNER JOIN geography.region r ON g.region_id = r.id
    INNER JOIN geography.timezone t ON g.timezone_id = t.id
WHERE
    account_id = %(account_id)s
