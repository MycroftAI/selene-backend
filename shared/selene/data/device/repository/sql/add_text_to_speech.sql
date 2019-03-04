INSERT INTO
    device.text_to_speech (setting_name, display_name, engine)
VALUES
    (%(setting_name)s, %(display_name)s, %(engine)s)
RETURNING id