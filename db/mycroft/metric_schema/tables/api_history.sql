CREATE TABLE metric.api_history (
    id          uuid        NOT NULL,
    http_method text        NOT NULL,
    http_status CHAR(3)     NOT NULL,
    duration    NUMERIC     NOT NULL,
    access_ts   timestamp   NOT NULL,
    api         text        NOT NULL,
    url         text        NOT NULL,
    account_id  uuid,
    device_id   uuid
)
PARTITION BY RANGE
    (access_ts)
