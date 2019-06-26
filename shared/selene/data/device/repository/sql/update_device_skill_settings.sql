UPDATE
    device.device_skill
SET
    skill_settings_display_id = %(settings_display_id)s,
    settings = %(settings_values)s
WHERE
    skill_id = %(skill_id)s
    AND device_id IN %(device_ids)s
