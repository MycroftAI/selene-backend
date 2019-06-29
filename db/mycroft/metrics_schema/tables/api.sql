CREATE TABLE metrics.api (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    url         text        NOT NULL,
    access_ts   timestamp   NOT NULL
            DEFAULT now(),
    api         text        NOT NULL,
    duration    NUMERIC     NOT NULL,
    http_status CHAR(3)     NOT NULL,
    account_id  uuid,
    device_id   uuid
);

CREATE INDEX IF NOT EXISTS
    api_access_ts_idx
ON
    metrics.api (access_ts)
;
