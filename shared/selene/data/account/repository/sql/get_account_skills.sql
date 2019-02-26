-- get all combinations of skills and skill setting meta for an account
WITH
    skill_meta AS (
        SELECT
            skill_id,
            display_name,
            max(branch)
        FROM
            skill.branch
        GROUP BY
            skill_id,
            display_name
    )
SELECT
    s.name AS skill_name,
    skm.display_name,
    d.name as device_name,
    sm.version,
    sm.settings_meta,
    ds.settings
FROM
    skill.skill s
    INNER JOIN device.device_skill ds on ds.skill_id = s.id
    INNER JOIN device.device d ON d.id = ds.device_id
    LEFT JOIN skill.setting_meta sm ON ds.skill_setting_meta_id = sm.id
    LEFT JOIN skill_meta skm ON skm.skill_id = s.id
WHERE
    d.account_id = %(account_id)s
ORDER BY
    s.name,
    sm.version
