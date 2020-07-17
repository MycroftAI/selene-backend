UPDATE
    metric.account_activity
SET
    open_dataset = open_dataset - 1,
    open_dataset_deleted = open_dataset_deleted + 1
WHERE
    activity_dt = current_date
