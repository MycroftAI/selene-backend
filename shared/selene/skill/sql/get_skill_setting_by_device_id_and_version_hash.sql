SELECT skill_set.* FROM device.device dev
JOIN device.device_skill dev_skill ON dev.id = dev_skill.device_id
JOIN device.skill_setting skill_set ON dev_skill.id = skill_set.device_skill_id
JOIN skill.skill skill ON dev_skill.skill_id = skill.id
JOIN skill.setting_version ver ON skill.id = ver.skill_id
WHERE ver.version_hash = %(setting_version_hash)s AND dev.id = %(device_id)s
