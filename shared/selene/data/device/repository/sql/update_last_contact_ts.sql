UPDATE
    device.device
SET
    last_contact_ts = now()
WHERE
    id = %(device_id)s
