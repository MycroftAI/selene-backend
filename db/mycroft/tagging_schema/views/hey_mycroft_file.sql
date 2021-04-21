CREATE MATERIALIZED VIEW tagging.hey_mycroft_file AS
    WITH not_speaking AS (
        SELECT
            t.id as tag_id,
            tv.id AS tag_value_id
        FROM
            tagging.tag t
                INNER JOIN tagging.tag_value tv ON t.id = tv.tag_id
        WHERE
                t.name = 'speaking'
            AND tv.value = 'no'
     ),
    file AS (
        -- Get all files for the specified wake word that have not been designated as noise
        SELECT
            wwf.id AS file_id,
            wwf.name AS file_name,
            fl.server,
            fl.directory,
            array_agg(wwfd.tag_id) AS designations
        FROM
            tagging.wake_word_file wwf
            INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
            INNER JOIN tagging.file_location fl ON fl.id = wwf.file_location_id
            LEFT JOIN tagging.wake_word_file_designation wwfd ON wwf.id = wwfd.wake_word_file_id
        WHERE
            ww.name = 'hey mycroft'
            AND (
                wwfd.tag_id IS NULL
                OR wwfd.tag_id::TEXT || wwfd.tag_value_id::TEXT != (
                    SELECT
                        tag_id::TEXT || tag_value_id::TEXT
                    FROM
                        not_speaking
               )
            )
        GROUP BY
            1, 2, 3, 4
    )
    SELECT
        f.file_id AS id,
        f.file_name as name,
        f.server,
        f.directory,
        f.designations
    FROM
        file AS f
    WHERE
        (f.designations IS NULL OR cardinality(f.designations) < 6)
    ORDER BY
        case when f.designations is null then 0 else cardinality(f.designations) end desc
    LIMIT 10000
