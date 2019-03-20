INSERT INTO
    device.wake_word (setting_name, display_name, account_id, engine)
VALUES
    (%(setting_name)s, %(display_name)s, %(account_id)s, %(engine)s)
RETURNING id
