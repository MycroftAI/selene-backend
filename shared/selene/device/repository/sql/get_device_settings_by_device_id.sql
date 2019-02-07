SELECT
  acc.id as uuid,
  acc.measurement_system as system_unit,
  acc.date_format as date_format,
  acc.time_format as time_format,
  json_build_object('setting_name', tts.setting_name, 'engine', tts.engine) as ttsSettings,
  json_build_object(
    'uuid', wk_word_st.id,
    'sampleRate', wk_word_st.sample_rate,
    'channels', wk_word_st.channels,
    'wakeWord', wk_word.wake_word,
    'phonemes', wk_word_st.pronunciation,
    'threshold', wk_word_st.threshold,
    'multiplier', wk_word_st.threshold_multiplier,
    'energyRatio', wk_word_st.dynamic_energy_ratio) as listenerSetting
FROM
  device.device dev
INNER JOIN
  device.account_preferences acc ON dev.account_id = acc.account_id
INNER JOIN
  device.text_to_speech tts ON acc.text_to_speech_id = tts.id
INNER JOIN
  device.wake_word wk_word ON acc.wake_word_id = wk_word.id
INNER JOIN
  device.wake_word_settings wk_word_st ON wk_word.id = wk_word_st.wake_word_id
WHERE
  dev.id = %(device_id)s