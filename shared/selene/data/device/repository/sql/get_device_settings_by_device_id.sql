SELECT
  acc.id as uuid,
  acc.measurement_system as system_unit,
  acc.date_format as date_format,
  acc.time_format as time_format,
  json_build_object('setting_name', tts.setting_name, 'engine', tts.engine) as tts_settings,
  json_build_object(
    'uuid', ps.id,
    'sampleRate', ps.sample_rate,
    'channels', ps.channels,
    'wakeWord', ww.name,
    'phonemes', ps.pronunciation,
    'threshold', ps.threshold,
    'multiplier', ps.threshold_multiplier,
    'energyRatio', ps.dynamic_energy_ratio) as listener_setting
FROM
  device.device dev
INNER JOIN
  device.account_preferences acc ON dev.account_id = acc.account_id
INNER JOIN
  device.text_to_speech tts ON dev.text_to_speech_id = tts.id
INNER JOIN
  wake_word.wake_word ww ON dev.wake_word_id = ww.id
LEFT JOIN
  wake_word.pocketsphinx_settings ps ON ww.id = ps.wake_word_id
WHERE
  dev.id = %(device_id)s
