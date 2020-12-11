-- Files containing audio data used to train wake word machine learning models.
CREATE TABLE tagging.wake_word_file (
    id                  uuid                        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                text                        NOT NULL UNIQUE,
    wake_word_id        uuid                        NOT NULL REFERENCES wake_word.wake_word,
    origin              tagging_file_origin_enum    NOT NULL,
    submission_date     date                        NOT NULL DEFAULT CURRENT_DATE,
    file_location_id    uuid                        NOT NULL REFERENCES tagging.file_location,
    account_id          uuid,
    status              tagging_file_status_enum    NOT NULL DEFAULT 'uploaded'::tagging_file_status_enum,
    insert_ts           TIMESTAMP                   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
