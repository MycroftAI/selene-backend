SELECT
    d.id,
    d.account_id,
    d.name,
    d.platform,
    d.enclosure_version,
    d.core_version,
    d.placement,
    d.last_contact_ts,
    d.insert_ts AS add_ts,
    json_build_object(
        'name', ww.name,
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
        'id', ctry.id,
        'name', ctry.name,
        'iso_code', ctry.iso_code
    ) AS country,
    json_build_object(
        'id', cty.id,
        'name', cty.name,
        'timezone', cty.name,
        'latitude', cty.latitude,
        'longitude', cty.longitude
    ) AS city,
    json_build_object(
        'id', r.id,
        'name', r.name,
        'region_code', r.region_code
    ) AS region,
    json_build_object(
        'id', tz.id,
        'name',tz.name,
        'dst_offset', tz.dst_offset,
        'gmt_offset', tz.gmt_offset
    ) AS timezone,
    json_build_object(
        'pantacor_id', pc.pantacor_id,
        'auto_update', pc.auto_update,
        'release', pc.release,
        'ssh_public_key', pc.ssh_public_key
    ) AS pantacor_config
FROM
    device.device d
    INNER JOIN wake_word.wake_word ww ON d.wake_word_id = ww.id
    INNER JOIN device.text_to_speech tts ON d.text_to_speech_id = tts.id
    INNER JOIN device.geography g ON d.geography_id = g.id
    INNER JOIN geography.country ctry ON g.country_id = ctry.id
    INNER JOIN geography.city cty ON g.city_id = cty.id
    INNER JOIN geography.region r ON g.region_id = r.id
    INNER JOIN geography.timezone tz ON g.timezone_id = tz.id
    LEFT OUTER JOIN device.pantacor_config pc on pc.device_id = d.id
WHERE
    d.id = %(device_id)s
