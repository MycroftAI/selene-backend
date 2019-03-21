INSERT INTO
    device.geography (account_id, country_id, region_id, city_id, timezone_id)
VALUES
    (
        %(account_id)s,
        (SELECT id FROM geography.country WHERE name = %(country)s),
        (
            SELECT
                r.id
            FROM
                geography.region r
                INNER JOIN geography.country c ON c.id = r.country_id
            WHERE
                r.name = %(region)s
                AND c.name = %(country)s
            ),
        (
            SELECT
                c.id
            FROM
                geography.city c
                INNER JOIN geography.region r ON r.id = c.region_id

            WHERE
                c.name = %(city)s
                AND r.name = %(region)s
            ),
        (SELECT id FROM geography.timezone WHERE name = %(timezone)s)
    )
RETURNING
    id
