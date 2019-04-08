WITH
    setting_display AS (
        SELECT
            s.id,
            sd.settings_display -> 'display_name' AS display_name,
            sd.settings_display -> 'skillMetadata' IS NOT NULL AS has_settings
        FROM
            skill.skill s
            LEFT JOIN skill.settings_display sd ON s.id = sd.skill_id
        GROUP BY
            s.id,
            settings_display
    )
SELECT DISTINCT
    json_build_object(
        'id', s.id,
        'skill_gid', s.skill_gid,
        'family_name', s.family_name,
        'has_settings', sm.has_settings,
        'display_name', sm.display_name
    )::jsonb as skill
FROM
    skill.skill s
    INNER JOIN device.device_skill ds ON ds.skill_id = s.id
    INNER JOIN device.device d ON d.id = ds.device_id
    INNER JOIN setting_display sm ON sm.id = s.id
WHERE
    d.account_id = %(account_id)s
