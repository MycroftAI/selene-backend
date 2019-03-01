SELECT
    sm.settings_meta::jsonb AS settings_definition,
    ds.settings::jsonb AS settings_values,
    array_agg(d.name) AS devices
FROM
    skill.setting_meta sm
    INNER JOIN device.device_skill ds ON sm.id = ds.skill_setting_meta_id
    INNER JOIN device.device d ON ds.device_id = d.id
WHERE
    sm.skill_id = %(skill_id)s
    AND d.account_id = %(account_id)s
GROUP BY
    sm.settings_meta::jsonb,
    ds.settings::jsonb
