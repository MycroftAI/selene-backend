SELECT
    skill.id,
    skill.name,
    meta.version,
    dev_skill.settings,
    meta.settings_meta
FROM
    device.device dev
INNER JOIN
    device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN
    skill.skill skill ON dev_skill.skill_id = skill.id
INNER JOIN
    skill.setting_meta meta ON dev_skill.skill_setting_meta_id = meta.id
WHERE
    dev.id = %(device_id)s AND meta.version = %(version_hash)s