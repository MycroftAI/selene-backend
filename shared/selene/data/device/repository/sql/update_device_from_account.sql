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
            device.wake_word
        WHERE
            display_name = %(wake_word)s
            AND (account_id IS NULL OR account_id = %(account_id)s)
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
