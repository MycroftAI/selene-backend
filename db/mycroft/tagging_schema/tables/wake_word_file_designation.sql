-- The final agreed upon value of a tag for a file.
CREATE TABLE tagging.wake_word_file_designation (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_file_id   uuid        NOT NULL REFERENCES tagging.wake_word_file,
    tag_id              uuid        NOT NULL REFERENCES tagging.tag,
    tag_value_id        uuid        NOT NULL REFERENCES tagging.tag_value,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_file_id, tag_id)
);
