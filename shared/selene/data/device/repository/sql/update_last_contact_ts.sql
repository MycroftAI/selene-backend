UPDATE
    device.device
SET
    last_contact_ts = %(last_contact_ts)s
WHERE
    id = %(device_id)s
