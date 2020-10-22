WITH undesignated_file_tag AS (
    SELECT
        wwft.wake_word_file_id,
        wwft.session_id
    FROM
        tagging.tag t
        LEFT JOIN tagging.wake_word_file_tag wwft ON t.id = wwft.tag_id
    WHERE
        t.id = %(tag_id)s
        AND wwft.wake_word_file_id NOT IN (
            SELECT
                wake_word_file_id
            FROM
                tagging.wake_word_file_designation
            WHERE
                tag_id = t.id
        )
)
SELECT
    wwf.id,
    wwf.name,
    fl.server,
    fl.directory
FROM
    tagging.wake_word_file wwf
    INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
    INNER JOIN tagging.file_location fl ON wwf.file_location_id = fl.id
    LEFT JOIN undesignated_file_tag uft ON uft.wake_word_file_id = wwf.id
WHERE
    ww.name = %(wake_word)s
    AND uft.session_id IS NULL
    OR uft.session_id != %(session_id)s
LIMIT 1
