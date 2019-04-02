WITH
    setting_meta AS (
        SELECT
            s.id,
            count(sd.id) > 0 AS has_settings
        FROM
            skill.skill s
            LEFT JOIN skill.settings_display sd ON s.id = sd.skill_id
        GROUP BY
            s.id
    )
SELECT DISTINCT
    json_build_object(
        'id', s.id,
        'skill_gid', s.skill_gid,
        'family_name', s.family_name,
        'has_settings', sm.has_settings
    )::jsonb as skill
FROM
    skill.skill s
    INNER JOIN device.device_skill ds ON ds.skill_id = s.id
    INNER JOIN device.device d ON d.id = ds.device_id
    INNER JOIN setting_meta sm ON sm.id = s.id
WHERE
    d.account_id = %(account_id)s
