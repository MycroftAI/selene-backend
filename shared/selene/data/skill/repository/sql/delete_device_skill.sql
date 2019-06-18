DELETE  FROM
    device.device_skill
WHERE
    id = (
        SELECT
            ds.id
        FROM
            device.device_skill ds
        INNER JOIN
            skill.skill s ON ds.skill_id = s.id
        WHERE
            ds.device_id = %(device_id)s AND s.skill_gid = %(skill_gid)s
    )