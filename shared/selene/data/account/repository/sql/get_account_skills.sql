-- get all combinations of skills and skill setting meta for an account
WITH
    skills AS (
        SELECT
            s.id AS skill_id,
            s.name AS skill_name,
            ds.skill_setting_meta_id,
            ds.settings::jsonb,
            array_agg(d.name) AS devices
        FROM
            skill.skill s
            INNER JOIN device.device_skill ds ON ds.skill_id = s.id
            INNER JOIN device.device d ON d.id = ds.device_id
        WHERE
            d.account_id = %(account_id)s
        GROUP BY
            s.id,
            s.name,
            ds.skill_setting_meta_id,
            ds.settings::jsonb
    ),
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
    s.skill_id,
    s.skill_name,
    s.settings,
    s.devices,
    skm.display_name,
    sm.version AS settings_version,
    sm.settings_meta
FROM
    skills s
    LEFT JOIN skill.setting_meta sm ON s.skill_setting_meta_id = sm.id
    LEFT JOIN skill_meta skm ON skm.skill_id = s.skill_id
