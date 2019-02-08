CREATE TABLE account.subscription (
    id              uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription    text    NOT NULL UNIQUE,
    rate            numeric NOT NULL,
    rate_period     text    NOT NULL
);
