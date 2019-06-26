SELECT
    id,
    measurement_system,
    date_format,
    time_format
FROM
    device.account_preferences
WHERE
    account_id = %(account_id)s
