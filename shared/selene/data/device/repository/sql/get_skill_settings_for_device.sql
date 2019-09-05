SELECT
    skill_settings_display_id AS settings_display_id,
    settings::jsonb AS settings_values,
    install_method,
    skill_id
FROM
    device.device_skill
WHERE
    device_id = %(device_id)s
    AND skill_id = %(skill_id)s
