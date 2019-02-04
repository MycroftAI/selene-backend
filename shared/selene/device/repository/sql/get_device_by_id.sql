SELECT
  dev.id,
  dev.name,
  dev.platform,
  dev.enclosure_version,
  dev.core_version,
  dev.placement,
  wk_word.id as wake_word_id,
  wk_word.wake_word,
  wk_word.engine,
  tts.id as text_to_speech_id,
  tts.setting_name,
  tts.display_name,
  tts.engine
FROM device.device dev
INNER JOIN
  device.wake_word wk_word ON dev.wake_word_id = wk_word.id
INNER JOIN
  device.text_to_speech tts ON dev.text_to_speech_id = tts.id
WHERE dev.id = %(device_id)s