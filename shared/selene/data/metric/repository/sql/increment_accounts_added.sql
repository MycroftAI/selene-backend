UPDATE
    metric.account_activity
SET
    accounts = accounts + 1,
    accounts_added = accounts_added + 1
WHERE
    activity_dt = current_date
