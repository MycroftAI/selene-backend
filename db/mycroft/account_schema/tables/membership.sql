CREATE TABLE account.membership (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    type            text        NOT NULL UNIQUE,
    rate            NUMERIC     NOT NULL,
    rate_period     text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
