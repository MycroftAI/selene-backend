WITH
    country AS (
        SELECT id FROM geography.country WHERE name = %(country)s
    ),
    region AS (
        SELECT
            r.id
        FROM
            geography.region r
            INNER JOIN geography.country c ON c.id = r.country_id
        WHERE
            r.name = %(region)s
            AND c.name = %(country)s

    ),
    city AS (
        SELECT
            c.id
        FROM
            geography.city c
            INNER JOIN geography.region r ON r.id = c.region_id

        WHERE
            c.name = %(city)s
            AND r.name = %(region)s
    ),
    timezone AS (
        SELECT id FROM geography.timezone WHERE name = %(timezone)s
    ),
    wake_word AS (
        SELECT id FROM wake_word.wake_word WHERE name = %(wake_word)s
    ),
    text_to_speech AS (
        SELECT id FROM device.text_to_speech WHERE display_name = %(voice)s
    )
INSERT INTO
    device.account_defaults (account_id, country_id, region_id, city_id, timezone_id, wake_word_id, text_to_speech_id)
VALUES
    (
        %(account_id)s,
        (SELECT id FROM country),
        (SELECT id FROM region),
        (SELECT id FROM city),
        (SELECT id FROM timezone),
        (SELECT id FROM wake_word),
        (SELECT id FROM text_to_speech)
    )
ON CONFLICT
    (account_id)
DO UPDATE SET
    country_id = (SELECT id FROM country),
    region_id = (SELECT id FROM region),
    city_id = (SELECT id FROM city),
    timezone_id = (SELECT id FROM timezone),
    wake_word_id = (SELECT id FROM wake_word),
    text_to_speech_id = (SELECT id FROM text_to_speech)
RETURNING
    id
