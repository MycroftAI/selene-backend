CREATE TABLE geography.country (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    iso_code    CHAR(2)     NOT NULL
            UNIQUE,
    name        text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL
            DEFAULT CURRENT_TIMESTAMP
)
