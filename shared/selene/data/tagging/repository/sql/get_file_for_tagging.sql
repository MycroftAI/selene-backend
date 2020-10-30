WITH wake_word_yes AS (
    SELECT
        tv.id
    FROM
        tagging.tag_value tv
        INNER JOIN tagging.tag t ON tv.tag_id = t.id
    WHERE
        t.name = 'wake word'
        AND tv.value = 'yes'
),
file_to_tag AS (
    SELECT
        wwf.id,
        wwf.name,
        fl.server,
        fl.directory,
        array_agg(row_to_json(wwfd.*)) AS designations
    FROM
        tagging.wake_word_file wwf
            INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
            INNER JOIN tagging.file_location fl ON fl.id = wwf.file_location_id
            LEFT JOIN tagging.wake_word_file_designation wwfd ON wwfd.wake_word_file_id = wwf.id
    WHERE
        ww.name = 'hey mycroft'
        AND (
            wwfd.tag_value_id IS NULL
            OR wwfd.tag_value_id = (SELECT id FROM wake_word_yes)
        )
    GROUP BY
        1, 2, 3, 4
)
SELECT
    *
FROM
    file_to_tag
WHERE
    cardinality(designations) < (SELECT count(*) FROM tagging.tag)
ORDER BY
    random()
LIMIT 1
