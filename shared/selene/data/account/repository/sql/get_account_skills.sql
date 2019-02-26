-- get all combinations of skills and skill setting meta for an account
SELECT
    s.name AS skill_name,
    d.name as device_name,
    sm.version,
    sm.settings_meta,
    ds.settings
FROM
    skill.skill s
    INNER JOIN device.device_skill ds on ds.skill_id = s.id
    INNER JOIN device.device d ON d.id = ds.device_id
    LEFT JOIN skill.setting_meta sm ON ds.skill_setting_meta_id = sm.id
WHERE
    d.account_id = %(account_id)s
ORDER BY
    s.name,
    sm.version
