SELECT
    ad.id,
    json_build_object(
        'id', cntry.id,
        'iso_code', cntry.iso_code,
        'name', cntry.name
    ) AS country,
    json_build_object(
        'id', r.id,
        'region_code', r.region_code,
        'name', r.name
    ) AS region,
    json_build_object(
        'id', cty.id,
        'name', cty.name,
        'latitude', cty.latitude,
        'longitude', cty.longitude,
        'timezone', tz.name
    ) AS city,
    json_build_object(
        'id', tz.id,
        'name', tz.name,
        'dst_offset', tz.dst_offset,
        'gmt_offset', tz.gmt_offset
    ) AS timezone,
    json_build_object(
        'id', ww.id,
        'name', ww.name,
        'engine', ww.engine
    ) AS wake_word,
    json_build_object(
        'id', tts.id,
        'setting_name', tts.setting_name,
        'display_name', tts.display_name,
        'engine', tts.engine
    ) AS voice
FROM
    device.account_defaults ad
    LEFT JOIN geography.country cntry ON cntry.id = ad.country_id
    LEFT JOIN geography.region r ON r.id = ad.region_id
    LEFT JOIN geography.city cty ON cty.id = ad.city_id
    LEFT JOIN geography.timezone tz ON tz.id = ad.timezone_id
    LEFT JOIN wake_word.wake_word ww ON ad.wake_word_id = ww.id
    LEFT JOIN device.text_to_speech tts ON ad.text_to_speech_id = tts.id
WHERE
    ad.account_id = %(account_id)s
