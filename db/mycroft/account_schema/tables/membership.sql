CREATE TABLE account.membership (
    id              uuid                    PRIMARY KEY
            DEFAULT gen_random_uuid(),
    type            membership_type_enum     NOT NULL
            UNIQUE,
    rate            NUMERIC                 NOT NULL,
    rate_period     text                    NOT NULL,
    insert_ts       TIMESTAMP               NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
