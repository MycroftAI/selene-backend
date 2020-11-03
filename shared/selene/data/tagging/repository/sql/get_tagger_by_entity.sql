SELECT
    id
FROM
    tagging.tagger
WHERE
    entity_type = %(entity_type)s
    AND entity_id = %(entity_id)s
