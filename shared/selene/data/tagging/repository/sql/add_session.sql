INSERT INTO
    tagging.session (tagger_id, session_ts_range)
VALUES
    (%(tagger_id)s, '[now,]'::tsrange)
RETURNING
    id
