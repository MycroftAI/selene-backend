SELECT
    accounts,
    accounts_added,
    accounts_deleted,
    accounts_active,
    members,
    members_added,
    members_expired,
    members_active,
    open_dataset,
    open_dataset_added,
    open_dataset_deleted,
    open_dataset_active
FROM
    metric.account_activity
WHERE
    activity_dt = %(activity_date)s
