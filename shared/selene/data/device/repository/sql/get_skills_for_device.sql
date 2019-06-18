SELECT
    d.name AS device_name,
    ds.id,
    ds.install_failure_reason,
    ds.install_method,
    ds.install_status,
    ds.install_ts,
    ds.skill_id,
    ds.update_ts,
    s.skill_gid
FROM
    device.device d
    INNER JOIN device.device_skill ds ON d.id = ds.device_id
    INNER JOIN skill.skill s ON ds.skill_id = s.id
WHERE
    d.id = %(device_id)s
