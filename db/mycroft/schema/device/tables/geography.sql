CREATE TABLE device.geography (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      uuid        NOT NULL
            REFERENCES account.account ON DELETE CASCADE,
    country_id      uuid        NOT NULL
            REFERENCES geography.country,
    region_id       uuid        NOT NULL
            REFERENCES geography.region,
    city_id         uuid        NOT NULL
            REFERENCES geography.city,
    timezone_id     uuid        NOT NULL
            REFERENCES geography.timezone,
    insert_ts       TIMESTAMP   NOT NULL
            DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, country_id, region_id, city_id, timezone_id)
);
