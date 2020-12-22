UPDATE
    device.device
SET
    name = %(name)s,
    placement = %(placement)s,
    geography_id = %(geography_id)s,
    wake_word_id = (
        SELECT
            id
        FROM
            wake_word.wake_word
        WHERE
            name = %(wake_word)s
        ORDER BY
            engine DESC
        LIMIT 1
    ),
    text_to_speech_id = (
        SELECT
            id
        FROM
            device.text_to_speech
        WHERE
            display_name = %(voice)s
    )
WHERE
    id = %(device_id)s
