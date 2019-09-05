UPDATE
    device.device_skill
SET
    skill_settings_display_id = %(settings_display_id)s,
    settings = %(settings_values)s
WHERE
    device_id = %(device_id)s
    AND skill_id = %(skill_id)s
