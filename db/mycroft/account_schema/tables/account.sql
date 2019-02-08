CREATE TABLE account.account (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    email_address       text    NOT NULL UNIQUE,
    username            text    NOT NULL UNIQUE,
    password            text
);
