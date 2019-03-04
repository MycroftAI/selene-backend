INSERT INTO
    device.device (account_id, name, wake_word_id, text_to_speech_id)
VALUES
    (%(account_id)s, %(name)s, %(wake_word_id)s, %(text_to_speech_id)s)
RETURNING id