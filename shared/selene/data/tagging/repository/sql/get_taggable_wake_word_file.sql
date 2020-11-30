-- Select a single file to be presented to the wake word tagger.
WITH file AS (
    -- Get all files for the specified wake word
    SELECT
        wwf.id AS file_id,
        wwf.name AS file_name,
        fl.server,
        fl.directory
    FROM
        tagging.wake_word_file wwf
        INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
        INNER JOIN tagging.file_location fl ON fl.id = wwf.file_location_id
    WHERE
        ww.name = %(wake_word)s
),
file_designation AS (
    -- Get all the designations assigned to the files
    SELECT
        f.file_id,
        array_agg(wwfd.tag_id) AS designations
    FROM
        file f
        INNER JOIN tagging.wake_word_file_designation wwfd ON f.file_id = wwfd.wake_word_file_id
    GROUP BY
        f.file_id
),
file_tag AS (
    -- Get all the file tags for tag types that have not been designated
    SELECT
        f.file_id,
        wwft.tag_id AS tag,
        array_agg(session_id) AS sessions
    FROM
        file f
        INNER JOIN tagging.wake_word_file_tag wwft ON f.file_id = wwft.wake_word_file_id
        LEFT JOIN file_designation fd ON f.file_id = fd.file_id
    WHERE
        array_position(fd.designations, wwft.tag_id) IS NULL
    GROUP BY
        f.file_id,
        wwft.tag_id
)
-- Use the results of the above nested table expressions to select a single file
-- that is not fully designated and has not already been tagged in the specified session.
SELECT
    f.file_id AS id,
    f.file_name as name,
    f.server,
    f.directory,
    fd.designations,
    ft.tag
FROM
    file AS f
    LEFT JOIN file_tag ft ON f.file_id = ft.file_id
    LEFT JOIN file_designation fd ON f.file_id = fd.file_id
WHERE
    (fd.designations IS NULL OR cardinality(fd.designations) < %(tag_count)s)
    AND array_position(ft.sessions, %(session_id)s) IS NULL
ORDER BY
    cardinality(ft.sessions)
LIMIT 1
