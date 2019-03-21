CREATE TABLE geography.city (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    region_id   uuid        NOT NULL
            REFERENCES geography.region,
    timezone_id uuid        NOT NULL
            REFERENCES geography.timezone,
    name        text        NOT NULL,
    latitude    NUMERIC     NOT NULL,
    longitude   NUMERIC     NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL
            DEFAULT CURRENT_TIMESTAMP

)
