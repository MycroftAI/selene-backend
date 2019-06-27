CREATE TABLE metrics.api_history (
    id          uuid        NOT NULL,
    url         text        NOT NULL,
    access_ts   timestamp   NOT NULL,
    api         text        NOT NULL,
    duration    INTEGER     NOT NULL,
    http_status CHAR(3)     NOT NULL,
    account_id  uuid,
    device_id   uuid,
    UNIQUE (url, access_ts)
)
PARTITION BY RANGE
    (access_ts)
