UPDATE
    metric.account_activity
SET
    members = members - 1,
    members_expired = members_expired + 1
WHERE
    activity_dt = current_date
