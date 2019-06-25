SELECT
    count(*) AS usage
FROM
    device.device_skill
WHERE
    skill_settings_display_id = %(settings_display_id)s
