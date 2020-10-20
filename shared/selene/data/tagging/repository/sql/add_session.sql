INSERT INTO
    tagging.session (tagger_id)
VALUES
    (%(tagger_id)s)
RETURNING
    id
