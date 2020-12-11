INSERT INTO
    tagging.tagger (entity_type, entity_id)
VALUES
    (%(entity_type)s, %(entity_id)s)
RETURNING
    id
