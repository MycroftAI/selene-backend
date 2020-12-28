CREATE TABLE metric.api (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    http_method text        NOT NULL,
    http_status CHAR(3)     NOT NULL,
    duration    NUMERIC     NOT NULL,
    access_ts   timestamp   NOT NULL
            DEFAULT now(),
    api         text        NOT NULL,
    url         text        NOT NULL,
    account_id  uuid,
    device_id   uuid
);

CREATE INDEX IF NOT EXISTS
    api_access_ts_idx
ON
    metric.api (access_ts)
;
