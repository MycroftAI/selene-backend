CREATE TABLE device.wake_word (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_name    text        NOT NULL,
    display_name    text        NOT NULL,
    account_id      uuid        REFERENCES account.account ON DELETE CASCADE,
    engine          text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, setting_name)
);
