-- Domain table for all known wake words currently in use or previously used.
CREATE TABLE wake_word.wake_word (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL,
    engine          text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, engine)
);
