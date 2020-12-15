-- Account level preferences that pertain to device function.
CREATE TABLE device.account_defaults (
    id                  uuid                    PRIMARY KEY
            DEFAULT gen_random_uuid(),
    account_id          uuid                    NOT NULL
            UNIQUE
            REFERENCES account.account ON DELETE CASCADE,
    wake_word_id        uuid
            REFERENCES wake_word.wake_word,
    text_to_speech_id   uuid
            REFERENCES device.text_to_speech,
    country_id          uuid
            REFERENCES geography.country,
    region_id           uuid
            REFERENCES geography.region,
    city_id             uuid
            REFERENCES geography.city,
    timezone_id         uuid
            REFERENCES geography.timezone,
    insert_ts           TIMESTAMP               NOT NULL
            DEFAULT CURRENT_TIMESTAMP

);
