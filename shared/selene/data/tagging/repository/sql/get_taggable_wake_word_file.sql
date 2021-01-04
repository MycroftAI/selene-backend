WITH file_tag AS (
    -- Get all the file tags for tag types that have not been designated
    SELECT
        f.id,
        wwft.tag_id AS tag,
        array_agg(session_id) AS sessions
    FROM
        tagging.{wake_word}_file f
            INNER JOIN tagging.wake_word_file_tag wwft ON f.id = wwft.wake_word_file_id
    WHERE
        array_position(f.designations, wwft.tag_id) IS NULL
    GROUP BY
        f.id,
        wwft.tag_id
)
-- Use the results of the above nested table expressions to select a single file
-- that is not fully designated and has not already been tagged in the specified session.
SELECT
    f.id,
    f.name,
    f.server,
    f.directory,
    f.designations,
    ft.tag,
    ft.sessions
FROM
    tagging.{wake_word}_file AS f
        LEFT JOIN file_tag ft ON f.id = ft.id
ORDER BY
    case when f.designations is null then 0 else cardinality(f.designations) end desc,
    case when ft.sessions is null then 0 else cardinality(ft.sessions) end desc
LIMIT 1
