CREATE TABLE device.location (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id  uuid        NOT NULL REFERENCES account.account ON DELETE CASCADE,
    country     text        NOT NULL,
    postal_code text        NOT NULL,
    time_zone   text,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, country, postal_code)
);
