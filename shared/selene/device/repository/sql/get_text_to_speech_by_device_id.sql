SELECT tts.* FROM device.text_to_speech tts
INNER JOIN device.device dev ON tts.id = dev.text_to_speech_id
WHERE dev.id = %(device_id)s