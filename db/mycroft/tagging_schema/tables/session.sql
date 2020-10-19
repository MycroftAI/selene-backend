-- A period of time a tagger spent tagging files.
CREATE TABLE tagging.session (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tagger_id           text        NOT NULL,
    session_ts_range    tsrange     NOT NULL DEFAULT '[now,]'::tsrange,
    note                text,
    insert_ts           timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    EXCLUDE USING gist (tagger_id WITH =, session_ts_range with &&),
    UNIQUE (tagger_id, session_ts_range)
)
