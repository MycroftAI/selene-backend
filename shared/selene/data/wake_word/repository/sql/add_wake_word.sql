INSERT INTO
    wake_word.wake_word (name, engine)
VALUES
    (%(name)s, %(engine)s)
RETURNING id
