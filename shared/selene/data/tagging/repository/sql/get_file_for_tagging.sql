WITH taggable_file AS (
    SELECT
        wwf.id,
        wwf.name,
        fl.server,
        fl.directory,
        max(ft.insert_ts) AS last_tag
    FROM
        tagging.wake_word_file wwf
        INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
        INNER JOIN tagging.file_location fl ON wwf.file_location_id = fl.id
        LEFT JOIN tagging.wake_word_file_tag ft ON wwf.id = ft.wake_word_file_id
    WHERE
        ww.name = 'hey mycroft'
        AND wwf.status NOT IN ('pending delete', 'deleted')
        AND ft.tag_id NOT IN (
            SELECT
                tag_id
            FROM
                tagging.wake_word_file_designation
            WHERE
                wake_word_file_id = wwf.id)
    GROUP BY
        1, 2, 3, 4
)
SELECT
    id,
    name,
    server,
    directory
FROM
    taggable_file
WHERE
    last_tag IS NULL
    or last_tag < CURRENT_TIMESTAMP - INTERVAL '1 hour'
LIMIT 1
