INSERT INTO
    device.wake_word (wake_word, account_id, engine)
VALUES
    (%(wake_word)s, %(account_id)s, %(engine)s)
RETURNING id