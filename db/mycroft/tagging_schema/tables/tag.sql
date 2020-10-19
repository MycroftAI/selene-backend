-- Represents all the ways data can be classified (i.e. tagged).
CREATE TABLE tagging.tag (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL UNIQUE,
    title           text        NOT NULL,
    instructions    text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
