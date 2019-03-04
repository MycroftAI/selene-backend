CREATE TABLE account.refresh_token (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid        NOT NULL REFERENCES account.account ON DELETE CASCADE,
    refresh_token       text,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, refresh_token)
);
