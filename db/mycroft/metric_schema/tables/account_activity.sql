CREATE TABLE metric.account_activity (
    id                  uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    activity_dt         date        NOT NULL
            DEFAULT current_date,
    accounts                INTEGER     NOT NULL,
    accounts_added          INTEGER     NOT NULL DEFAULT 0,
    accounts_deleted        INTEGER     NOT NULL DEFAULT 0,
    accounts_active         INTEGER     NOT NULL DEFAULT 0,
    members                 INTEGER     NOT NULL,
    members_added           INTEGER     NOT NULL DEFAULT 0,
    members_expired         INTEGER     NOT NULL DEFAULT 0,
    members_active          INTEGER     NOT NULL DEFAULT 0,
    open_dataset            INTEGER     NOT NULL,
    open_dataset_added      INTEGER     NOT NULL DEFAULT 0,
    open_dataset_deleted    INTEGER     NOT NULL DEFAULT 0,
    open_dataset_active     INTEGER     NOT NULL DEFAULT 0,
    insert_ts               timestamp   NOT NULL
            DEFAULT now()
);

CREATE INDEX IF NOT EXISTS
    account_activity_dt_idx
ON
    metric.account_activity (activity_dt)
;
