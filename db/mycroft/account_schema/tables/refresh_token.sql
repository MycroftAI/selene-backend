CREATE TABLE account.refresh_token (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid    NOT NULL REFERENCES account.account ON DELETE CASCADE,
    refresh_token       text,
    UNIQUE (account_id, refresh_token)
);
