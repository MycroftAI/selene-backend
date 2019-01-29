SELECT settings.* FROM device.wake_word_settings settings
INNER JOIN device.wake_word wk_word ON settings.wake_word_id = wk_word.id
INNER JOIN device.device dev ON wk_word.id = dev.wake_word_id
WHERE dev.id = %(device_id)s