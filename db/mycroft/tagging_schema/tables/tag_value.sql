-- Represents all the ways data can be classified (i.e. tagged).
CREATE TABLE tagging.tag_value (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_id          uuid        NOT NULL REFERENCES tagging.tag,
    value           text        NOT NULL,
    display         text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tag_id, value)
);
