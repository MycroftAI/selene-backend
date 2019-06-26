DELETE FROM
    device.device_skill
WHERE
    device_id = %(device_id)s
    AND skill_id = (SELECT id FROM skill.skill WHERE skill_gid = %(skill_gid)s)
