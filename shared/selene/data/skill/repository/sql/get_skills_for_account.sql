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
    ),
    skill_versions AS (
        SELECT
            s.id as skill_id,
            array_agg(
                json_build_object(
                    'version', b.branch,
                    'display_name', b.display_name
                )
            ) AS versions
        FROM
            skill.skill s
            INNER JOIN skill.branch b ON s.id = b.skill_id
        GROUP BY
            s.id
    )
SELECT DISTINCT
    json_build_object(
        'id', s.id,
        'name', s.name,
        'url', s.url,
        'has_settings', sm.has_settings,
        'versions', sv.versions
    )::jsonb as skill
FROM
    skill.skill s
    INNER JOIN device.device_skill ds ON ds.skill_id = s.id
    INNER JOIN device.device d ON d.id = ds.device_id
    INNER JOIN setting_meta sm ON sm.id = s.id
    LEFT JOIN skill_versions sv ON sv.skill_id = s.id
WHERE
    d.account_id = %(account_id)s
