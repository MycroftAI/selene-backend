SELECT
    sd.settings_display::jsonb AS settings_display,
    ds.settings::jsonb AS settings_values,
    array_agg(d.name) AS devices
FROM
    skill.settings_display sd
    INNER JOIN device.device_skill ds ON sd.id = ds.skill_settings_display_id
    INNER JOIN device.device d ON ds.device_id = d.id
WHERE
    sd.skill_id = %(skill_id)s
    AND d.account_id = %(account_id)s
GROUP BY
    sd.settings_display::jsonb,
    ds.settings::jsonb
