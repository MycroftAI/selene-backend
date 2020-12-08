SELECT
    platform,
    paired,
    connected
FROM
    metric.device_activity
WHERE
    activity_dt = %(activity_date)s
