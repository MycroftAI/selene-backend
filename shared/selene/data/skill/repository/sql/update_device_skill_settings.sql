UPDATE
    device.device_skill
SET
    settings = %(settings_values)s
WHERE
    skill_id = %(skill_id)s
    AND device_id IN (
        SELECT id FROM device.device WHERE name IN %(device_names)s
    )
