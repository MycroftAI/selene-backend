UPDATE
    metric.device_activity
SET
    connected = connected + 1
WHERE
    activity_dt = current_date
    AND platform = %(platform)s
