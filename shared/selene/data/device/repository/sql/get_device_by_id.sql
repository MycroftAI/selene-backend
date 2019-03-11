SELECT
  dev.id,
  dev.name,
  dev.platform,
  dev.enclosure_version,
  dev.core_version,
  dev.placement,
  dev.account_id
FROM device.device dev
INNER JOIN
  device.wake_word wk_word ON dev.wake_word_id = wk_word.id
INNER JOIN
  device.text_to_speech tts ON dev.text_to_speech_id = tts.id
WHERE dev.id = %(device_id)s