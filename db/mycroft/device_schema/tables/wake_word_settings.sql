-- Settings for wake words using the Pocketsphinx engine
CREATE TABLE device.wake_word_settings (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_id            uuid        UNIQUE REFERENCES device.wake_word ON DELETE CASCADE,
    sample_rate             integer,
    channels                integer,
    pronunciation           text,
    threshold               text,
    threshold_multiplier    numeric,
    dynamic_energy_ratio    numeric
);
