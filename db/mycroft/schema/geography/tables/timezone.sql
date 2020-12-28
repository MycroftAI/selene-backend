CREATE TABLE geography.timezone (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    country_id  uuid        NOT NULL
            REFERENCES geography.country,
    name        text        NOT NULL UNIQUE,
    gmt_offset  NUMERIC     NOT NULL,
    dst_offset  NUMERIC,
    insert_ts   TIMESTAMP   NOT NULL
            DEFAULT CURRENT_TIMESTAMP
)
