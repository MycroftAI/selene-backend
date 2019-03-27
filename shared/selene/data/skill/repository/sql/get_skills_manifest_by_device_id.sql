SELECT
    dev_skill.install_method as origin,
    dev_skill.install_status as installation,
    dev_skill.install_failure_reason as failure_message,
    dev_skill.install_ts as installed,
    dev_skill.update_ts as updated,
    skill.name as name
FROM
    device.device dev
INNER JOIN
    device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN
    skill.skill ON dev_skill.skill_id = skill.id
WHERE
    dev.id = %(device_id)s