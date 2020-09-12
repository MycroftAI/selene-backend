-- The Pocketsphinx wake word settings in use by each account.
CREATE TABLE wake_word.pocketsphinx_settings (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_id            uuid        REFERENCES wake_word.wake_word ON DELETE CASCADE,
    account_id              uuid        REFERENCES account.account ON DELETE CASCADE,
    sample_rate             INTEGER,
    channels                INTEGER,
    pronunciation           text,
    threshold               text,
    threshold_multiplier    NUMERIC,
    dynamic_energy_ratio    NUMERIC,
    insert_ts               TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_id, account_id)
);
