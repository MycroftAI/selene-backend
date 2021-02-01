UPDATE
    device.pantacor_config
SET
    ssh_public_key = %(ssh_public_key)s,
    auto_update = %(auto_update)s,
    release = %(release)s
WHERE
    device_id = %(device_id)s
