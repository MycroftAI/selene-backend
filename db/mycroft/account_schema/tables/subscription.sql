CREATE TABLE account.subscription (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription    text        NOT NULL UNIQUE,
    rate            NUMERIC     NOT NULL,
    rate_period     text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
