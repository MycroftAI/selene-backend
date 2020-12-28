UPDATE
    tagging.session
SET
    session_ts_range = tsrange(lower(session_ts_range), %(end_ts)s)
WHERE
    id = %(session_id)s
