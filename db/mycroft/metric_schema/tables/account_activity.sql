CREATE TABLE metric.account_activity (
    id                  uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    activity_dt         date        NOT NULL
            DEFAULT current_date,
    added               INTEGER     NOT NULL,
    deleted             INTEGER     NOT NULL,
    active              INTEGER     NOT NULL,
    active_open_dataset INTEGER     NOT NULL,
    active_member       INTEGER     NOT NULL,
    insert_ts           timestamp   NOT NULL
            DEFAULT current_timestamp
);

CREATE INDEX IF NOT EXISTS
    account_activity_dt_idx
ON
    metric.account_activity (activity_dt)
;
