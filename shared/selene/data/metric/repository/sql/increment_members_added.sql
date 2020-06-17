UPDATE
    metric.account_activity
SET
    members = members + 1,
    members_added = members_added + 1
WHERE
    activity_dt = current_date
