SELECT
    dds.skill_settings_display_id AS settings_display_id,
    dds.settings::jsonb AS settings_values,
    dds.install_method,
    dds.skill_id,
    array_agg(dds.device_id::text) AS device_ids
FROM
    device.device dd
    INNER JOIN device.device_skill dds ON dd.id = dds.device_id
WHERE
    dd.account_id = %(account_id)s
    AND dds.skill_id = %(skill_id)s
GROUP BY
    dds.skill_settings_display_id,
    dds.settings::jsonb,
    dds.install_method,
    dds.skill_id
