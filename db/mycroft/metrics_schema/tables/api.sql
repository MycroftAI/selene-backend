CREATE TABLE metrics.api (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    url         text        NOT NULL,
    access_ts   timestamp   NOT NULL
            DEFAULT now(),
    api         text        NOT NULL,
    duration    INTEGER     NOT NULL,
    http_status CHAR(3)     NOT NULL,
    account_id  uuid,
    UNIQUE (url, access_ts)
)
