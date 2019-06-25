DELETE FROM
    device.device_skill
WHERE
    device_id = %(device_id)s
    AND skill_id = %(skill_id)s
