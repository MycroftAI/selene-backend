INSERT INTO
    device.device_skill (
        device_id,
        skill_id,
        install_method,
        install_status,
        install_failure_reason,
        install_ts,
        update_ts
    )
VALUES
    (
        %(device_id)s,
        %(skill_id)s,
        %(install_method)s,
        %(install_status)s,
        %(install_failure_reason)s,
        %(install_ts)s,
        %(update_ts)s
    )
RETURNING
    id
