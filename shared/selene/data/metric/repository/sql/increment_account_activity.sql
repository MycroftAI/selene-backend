UPDATE
    metric.account_activity
SET
    accounts_active = accounts_active + 1,
    members_active = members_active + %(member_increment)s,
    open_dataset_active = open_dataset_active + %(open_dataset_increment)s
WHERE
    activity_dt = current_date
