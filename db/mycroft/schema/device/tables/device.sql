CREATE TABLE device.device (
    id                  uuid            PRIMARY KEY
            DEFAULT gen_random_uuid(),
    account_id          uuid            NOT NULL
            REFERENCES account.account ON DELETE CASCADE ,
    name                text            NOT NULL,
    platform            text            NOT NULL
            DEFAULT 'unknown',
    enclosure_version   text            NOT NULL
            DEFAULT 'unknown',
    core_version        text            NOT NULL
            DEFAULT 'unknown',
    wake_word_id        uuid            NOT NULL
            REFERENCES wake_word.wake_word,
    text_to_speech_id   uuid            NOT NULL
            REFERENCES device.text_to_speech,
    category_id         uuid
            REFERENCES device.category,
    geography_id        uuid            NOT NULL
            REFERENCES device.geography,
    placement           text,
    last_contact_ts     timestamp,
    insert_ts           TIMESTAMP       NOT NULL
            DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, name)
);
