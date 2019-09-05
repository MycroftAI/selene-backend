SELECT
    ds.skill_settings_display_id AS settings_display_id,
    ds.settings::jsonb AS settings_values,
    ds.skill_id,
    s.skill_gid
FROM
    device.device_skill ds
    INNER JOIN skill.skill s ON ds.skill_id = s.id
WHERE
    device_id = %(device_id)s
