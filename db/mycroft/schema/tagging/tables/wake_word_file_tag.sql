-- Represents all the ways data can be classified (i.e. tagged).
CREATE TABLE tagging.wake_word_file_tag (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_file_id   uuid    NOT NULL REFERENCES tagging.wake_word_file,
    session_id      uuid        NOT NULL REFERENCES tagging.session,
    tag_id          uuid        NOT NULL REFERENCES tagging.tag,
    tag_value_id    uuid        NOT NULL REFERENCES tagging.tag_value,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_file_id, session_id, tag_id)
);
