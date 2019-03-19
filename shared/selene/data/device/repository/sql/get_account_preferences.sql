SELECT
    ap.id,
    ap.measurement_system,
    ap.date_format,
    ap.time_format,
    ctry.name AS country,
    r.name AS region,
    cty.name as city,
    tz.name as timezone,
    json_build_object(
        'id', ww.id,
        'wake_word', ww.wake_word,
        'engine', ww.engine
    ) AS wake_word,
    json_build_object(
        'id', tts.id,
        'setting_name', tts.setting_name,
        'display_name', tts.display_name,
        'engine', tts.engine
    ) AS voice
FROM
    device.account_preferences ap
    LEFT JOIN device.wake_word ww ON ap.wake_word_id = ww.id
    LEFT JOIN device.text_to_speech tts ON ap.text_to_speech_id = tts.id
    LEFT JOIN geography.country ctry ON ap.country_id = ctry.id
    LEFT JOIN geography.city cty ON ap.city_id = cty.id
    LEFT JOIN geography.region r ON ap.region_id = r.id
    LEFT JOIN geography.timezone tz ON ap.timezone_id = tz.id
WHERE
    ap.account_id = %(account_id)s
