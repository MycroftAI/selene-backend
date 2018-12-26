SELECT set_section.* FROM device.device dev
INNER JOIN device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN skill.skill skill ON dev_skill.skill_id = skill.id
INNER JOIN skill.setting_version set_version ON skill.id = set_version.skill_id
INNER JOIN skill.setting_section set_section ON set_version.id = set_section.skill_version_id
WHERE dev.id = %(device_id)s AND set_version.version_hash =  %(setting_version_hash)s