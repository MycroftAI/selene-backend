SELECT
    s.id,
    max(ft.insert_ts) AS last_tag_ts
FROM
    tagging.session s
    LEFT JOIN tagging.wake_word_file_tag ft ON s.id = ft.session_id
WHERE
    tagger_id = (
        SELECT
            id::text
        FROM
            tagging.tagger
        WHERE
            entity_type = 'account'
            AND entity_id = %(entity_id)s
    )
    AND upper(session_ts_range) IS NULL
GROUP BY
    1
