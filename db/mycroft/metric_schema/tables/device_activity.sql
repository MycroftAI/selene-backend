CREATE TABLE metric.device_activity (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_dt     date        NOT NULL DEFAULT current_date,
    platform         text        NOT NULL,
    paired          INTEGER     NOT NULL DEFAULT 0,
    connected       INTEGER     NOT NULL DEFAULT 0,
    insert_ts       timestamp   NOT NULL DEFAULT now(),
    UNIQUE (activity_dt, platform)
);
