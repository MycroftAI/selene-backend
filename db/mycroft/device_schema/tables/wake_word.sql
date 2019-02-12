CREATE TABLE device.wake_word (
    id                      uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word               text    NOT NULL,
    account_id              uuid    REFERENCES account.account ON DELETE CASCADE,
    engine                  text    NOT NULL,
    UNIQUE (account_id, wake_word)
);