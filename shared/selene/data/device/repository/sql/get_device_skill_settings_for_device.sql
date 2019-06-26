SELECT
    skill_settings_display_id AS settings_display_id,
    settings::jsonb AS settings_values,
    install_method,
    skill_id,
    array_agg(device_id::text) AS device_ids
FROM
    device.device_skill
WHERE
    device_id = %(device_id)s
GROUP BY
    skill_settings_display_id,
    settings::jsonb,
    install_method,
    skill_id
