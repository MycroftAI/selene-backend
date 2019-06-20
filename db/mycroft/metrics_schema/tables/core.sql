CREATE TABLE metrics.core (
    id              uuid        PRIMARY KEY
        DEFAULT gen_random_uuid(),
    device_id       uuid        NOT NULL
        REFERENCES device.device
        ON DELETE CASCADE,
    metric_type     text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL
        DEFAULT now(),
    metric_value    json        NOT NULL,
    UNIQUE (device_id, insert_ts)
)
