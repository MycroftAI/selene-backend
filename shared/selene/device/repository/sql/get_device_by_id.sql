SELECT
  dev.id,
  dev.name,
  dev.platform,
  dev.enclosure_version,
  dev.core_version,
  dev.placement,
  json_build_object('id', wk_word.id, 'wake_word', wk_word.wake_word, 'engine', wk_word.engine) as wake_word,
  json_build_object('id', tts.id, 'setting_name', tts.setting_name, 'display_name', tts.display_name, 'engine', tts.engine) as text_to_speech
FROM device.device dev
INNER JOIN
  device.wake_word wk_word ON dev.wake_word_id = wk_word.id
INNER JOIN
  device.text_to_speech tts ON dev.text_to_speech_id = tts.id
WHERE dev.id = %(device_id)s