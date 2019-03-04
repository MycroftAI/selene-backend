CREATE TABLE device.text_to_speech (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_name    text            NOT NULL UNIQUE,
    display_name    text            NOT NULL,
    engine          tts_engine_enum NOT NULL,
    insert_ts       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);
