INSERT INTO
    device.device_skill (device_id, skill_id, skill_settings_display_id, settings)
VALUES
    (%(device_id)s, %(skill_id)s, %(skill_settings_display_id)s, %(settings_value)s)
ON CONFLICT ON CONSTRAINT
    device_skill_device_id_skill_id_key
DO UPDATE SET
    skill_settings_display_id = %(skill_settings_display_id)s,
    settings = %(settings_value)s