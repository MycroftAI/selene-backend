SELECT skill.id as skill_id, skill.name, set_version.id AS skill_version_id, set_version.version_hash FROM device.device dev
INNER JOIN device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN skill.skill ON dev_skill.skill_id = skill.id
INNER JOIN skill.setting_version set_version ON skill.id = set_version.skill_id
WHERE dev.id = %(device_id)s