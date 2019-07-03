INSERT INTO
    device.device_skill (
        device_id,
        skill_id,
        skill_settings_display_id,
        settings
    )
VALUES
    (
        %(device_id)s,
        %(skill_id)s,
        %(settings_display_id)s,
        %(settings_values)s
    )
ON CONFLICT
    (device_id, skill_id)
DO UPDATE SET
    skill_settings_display_id = %(settings_display_id)s,
    settings = %(settings_values)s
