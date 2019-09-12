SELECT
    dds.skill_id,
    dds.settings AS settings_values,
    ssd.settings_display
FROM
    device.device_skill dds
    INNER JOIN skill.skill ss ON dds.skill_id = ss.id
    INNER JOIN skill.settings_display ssd ON dds.skill_settings_display_id = ssd.id
WHERE
    dds.device_id = %(device_id)s
