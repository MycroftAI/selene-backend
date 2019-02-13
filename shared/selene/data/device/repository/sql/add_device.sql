INSERT INTO
    device.device (account_id, name, wake_word_id, text_to_speech_id)
SELECT
    %(account_id)s,
    %(name)s,
    pref.wake_word_id,
    pref.text_to_speech_id
FROM
    account.account acc
INNER JOIN
    device.account_preferences pref ON acc.id = pref.account_id
WHERE
    acc.id = %(account_id)s
RETURNING id