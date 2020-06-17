DELETE FROM
    metric.account_activity
WHERE
    activity_dt = %(activity_date)s
