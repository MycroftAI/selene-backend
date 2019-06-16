UPDATE
    device.device_skill
SET
    settings = %(settings_values)s
WHERE
    skill_id IN %(skill_id)s
    AND device_id IN (
        SELECT
            id
        FROM
            device.device
        WHERE
            account_id = %(account_id)s
            AND name IN %(device_names)s
    )
