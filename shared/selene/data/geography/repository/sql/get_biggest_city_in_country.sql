SELECT
    cty.latitude,
    cty.longitude,
    cty.name AS city,
    cntry.name AS country,
    r.name AS region,
    t.name AS timezone
FROM
    geography.city cty
    INNER JOIN geography.region r ON cty.region_id = r.id
    INNER JOIN geography.country cntry ON r.country_id = cntry.id
    INNER JOIN geography.timezone t ON cty.timezone_id = t.id
WHERE
    lower(cntry.name) = %(country)s
    AND cty.population IS NOT NULL
ORDER BY
    cty.population DESC
LIMIT
    1

