SELECT
    d.name AS device_name,
    ds.id,
    ds.install_failure_reason,
    ds.install_method,
    ds.install_status,
    ds.install_ts,
    ds.skill_id
FROM
    device.device d
    INNER JOIN device.device_skill ds ON d.id = ds.device_id
WHERE
    d.account_id = %(account_id)s
