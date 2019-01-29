SELECT * FROM device.wake_word wk_word
INNER JOIN device.device dev ON wk_word.id = dev.wake_word_id
WHERE dev.id = %(device_id)s