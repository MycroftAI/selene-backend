SELECT
    id
FROM
    wake_word.wake_word
WHERE
    name = %(name)s
    AND engine = %(engine)s
