UPDATE
    metric.account_activity
SET
    accounts = accounts - 1,
    accounts_deleted = accounts_deleted + 1
WHERE
    activity_dt = current_date
