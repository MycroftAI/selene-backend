INSERT INTO
    device.device (account_id, name, placement, wake_word_id, text_to_speech_id, geography_id)
VALUES
    (
        %(account_id)s,
        %(name)s,
        %(placement)s,
        (
            SELECT
                id
            FROM
                device.wake_word
            WHERE
                (account_id IS NULL OR account_id = %(account_id)s)
                AND display_name = %(wake_word)s
        ),
        (SELECT id FROM device.text_to_speech WHERE display_name = %(voice)s),
        (
            SELECT
                g.id
            FROM
                device.geography g
                INNER JOIN geography.country cntry ON cntry.id = g.country_id
                INNER JOIN geography.region r ON r.id = g.region_id
                INNER JOIN geography.city cty ON cty.id = g.city_id
                INNER JOIN geography.timezone tz ON tz.id = g.timezone_id
            WHERE
                g.account_id = %(account_id)s
                AND cntry.name = %(country)s
                AND r.name = %(region)s
                AND cty.name = %(city)s
                AND tz.name = %(timezone)s
        )
    )
RETURNING id
