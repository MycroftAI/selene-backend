SELECT DISTINCT
    ss.family_name,
    sd.id AS market_id,
    ssd.settings_display -> 'skillMetadata' IS NOT NULL AS has_settings,
    ssd.settings_display -> 'display_name' AS display_name,
    array_agg(ss.id) AS skill_ids
FROM
    skill.skill ss
    INNER JOIN device.device_skill dds ON dds.skill_id = ss.id
    INNER JOIN device.device dd ON dd.id = dds.device_id
    LEFT JOIN skill.display sd ON ss.id = sd.skill_id
    LEFT JOIN skill.settings_display ssd ON ssd.skill_id = ss.id
WHERE
    dd.account_id = %(account_id)s
GROUP BY
    1, 2, 3, 4
