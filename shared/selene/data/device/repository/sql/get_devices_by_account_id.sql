SELECT
    d.id,
    d.name,
    d.platform,
    d.enclosure_version,
    d.core_version,
    d.placement,
    d.last_contact_ts,
    json_build_object(
        'wake_word', ww.wake_word,
        'engine', ww.engine,
        'id', ww.id
    ) AS wake_word,
    json_build_object(
        'setting_name', tts.setting_name,
        'display_name', tts.display_name,
        'engine', tts.engine,
        'id', tts.id
    ) AS text_to_speech,
    json_build_object(
        'id', g.id,
        'country', g.country,
        'time_zone', g.time_zone
    ) AS geography
FROM
    device.device d
    INNER JOIN device.wake_word ww ON d.wake_word_id = ww.id
    INNER JOIN device.text_to_speech tts ON d.text_to_speech_id = tts.id
    LEFT JOIN device.geography g ON d.geography_id = g.id
WHERE
    d.account_id = %(account_id)s
