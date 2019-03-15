SELECT
    c.id,
    c.name,
    c.latitude,
    c.longitude,
    t.name as timezone
FROM
    geography.city c
    INNER JOIN geography.timezone t ON c.timezone_id = t.id
WHERE
    region_id = %(region_id)s
