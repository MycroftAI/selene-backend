UPDATE
    device.device_skill
SET
    settings = %(settings)s
WHERE
    device_id IN (
        SELECT
            id
        FROM
            device.device
        WHERE
            account_id = %(account_id)s AND
            device_name IN %(device_names)s
    )
    AND skill_id = (SELECT id from skill.skill WHERE name = %(skill_name)s)
