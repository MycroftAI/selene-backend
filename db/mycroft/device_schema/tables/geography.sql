CREATE TABLE device.geography (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id  uuid        NOT NULL REFERENCES account.account ON DELETE CASCADE,
    country     text        NOT NULL,
    state       text        NOT NULL,
    city        text        NOT NULL,
    time_zone   text,
    latitude    NUMERIC     NOT NULL,
    longitude   NUMERIC     NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, latitude, longitude)
);
