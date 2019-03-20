SELECT
    ap.id,
    ap.measurement_system,
    ap.date_format,
    ap.time_format
FROM
    device.account_preferences ap
WHERE
    ap.account_id = %(account_id)s
