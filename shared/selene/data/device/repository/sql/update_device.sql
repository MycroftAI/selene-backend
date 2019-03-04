UPDATE
    device.device
SET
    platform = %(platform)s,
    enclosure_version = %(enclosure_version)s,
    core_version = %(core_version)s
WHERE
    id = %(device_id)s