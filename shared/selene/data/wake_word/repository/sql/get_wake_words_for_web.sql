SELECT
    ww.id,
    ww.name,
    ww.engine
FROM
    wake_word.wake_word ww
    INNER JOIN wake_word.pocketsphinx_settings ps ON ww.id = ps.wake_word_id
WHERE
    ps.account_id is NULL
