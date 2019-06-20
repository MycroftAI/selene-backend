UPDATE
    device.device_skill
SET
    install_method = %(install_method)s,
    install_status = %(install_status)s,
    install_failure_reason = %(failure_message)s,
    install_ts = %(install_ts)s,
    update_ts = %(update_ts)s
WHERE
    device_id = %(device_id)s
    AND skill_id = (
        SELECT
            id
        FROM
            skill.skill
        WHERE
            skill_gid = %(skill_gid)s
    )
