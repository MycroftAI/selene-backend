-- Account level preferences that pertain to device function.
CREATE TABLE device.account_preferences (
    id                  uuid                    PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid                    REFERENCES account.account ON DELETE CASCADE,
    date_format         date_format_enum        NOT NULL DEFAULT 'MM/DD/YYYY',
    time_format         time_format_enum        NOT NULL DEFAULT '12 Hour',
    measurement_system  measurement_system_enum NOT NULL DEFAULT  'Imperial',
    wake_word_id        uuid                    NOT NULL REFERENCES device.wake_word,
    text_to_speech_id   uuid                    NOT NULL REFERENCES device.text_to_speech,
    geography_id         uuid                   REFERENCES device.geography,
    insert_ts           TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP

);
