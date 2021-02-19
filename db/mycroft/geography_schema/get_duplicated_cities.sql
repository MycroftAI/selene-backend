-- Query to get a list of duplicated cities for use in a process to remove them.
WITH duplicated_cities AS (
    SELECT
        c.name AS country_name,
        r.name AS region_name,
        y.name AS city_name,
        array_agg(y.id::text) as city_ids
    FROM
        geography.city y
        INNER JOIN geography.region r on r.id = y.region_id
        INNER JOIN geography.country c on c.id = r.country_id
    GROUP BY
        1, 2, 3
)
SELECT
    *
FROM
    duplicated_cities
WHERE
    cardinality(city_ids) > 1
;
