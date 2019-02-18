CREATE TABLE account.account (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    email_address       text        NOT NULL UNIQUE,
    display_name       text        NOT NULL UNIQUE,
    password            text,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
