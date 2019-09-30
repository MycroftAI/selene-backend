SELECT
    sd.settings_display::jsonb -> 'skillMetadata' AS settings_definition,
    ds.settings::jsonb AS settings_values,
    array_agg(d.name) AS device_names
FROM
    device.device_skill ds
    INNER JOIN device.device d ON ds.device_id = d.id
    INNER JOIN skill.skill s ON ds.skill_id = s.id
    LEFT JOIN skill.settings_display sd ON ds.skill_settings_display_id = sd.id
WHERE
    s.family_name = %(family_name)s
    AND d.account_id = %(account_id)s
GROUP BY
    settings_definition,
    settings_values
