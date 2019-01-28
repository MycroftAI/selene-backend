SELECT skill_set.* FROM device.device dev
INNER JOIN device.device_skill dev_skill ON dev_skill.device_id = dev.id
INNER JOIN device.skill_setting skill_set ON dev_skill.id = skill_set.device_skill_id
WHERE dev.id = %(device_id)s
