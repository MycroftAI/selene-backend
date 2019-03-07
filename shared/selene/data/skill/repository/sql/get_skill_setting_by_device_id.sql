SELECT
    skill.id,
    dev_skill.settings,
    display.settings_display
FROM
    device.device dev
INNER JOIN
    device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN
    skill.skill skill ON dev_skill.skill_id = skill.id
INNER JOIN
    skill.settings_display display ON dev_skill.skill_settings_display_id = display.id
WHERE
    dev.id = %(device_id)s