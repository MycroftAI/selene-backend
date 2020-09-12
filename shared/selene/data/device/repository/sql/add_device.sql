INSERT INTO
    device.device (account_id, name, placement, wake_word_id, text_to_speech_id, geography_id)
VALUES
    (
        %(account_id)s,
        %(name)s,
        %(placement)s,
        (SELECT id FROM wake_word.wake_word WHERE name = %(wake_word)s),
        (SELECT id FROM device.text_to_speech WHERE display_name = %(voice)s),
        %(geography_id)s
    )
RETURNING id
