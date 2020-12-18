SELECT
    ww.name AS wake_word,
    wwft.wake_word_file_id,
    wwft.session_id,
    wwft.tag_id,
    wwft.tag_value_id
FROM
    tagging.wake_word_file wwf
        INNER JOIN wake_word.wake_word ww ON wwf.wake_word_id = ww.id
        INNER JOIN tagging.wake_word_file_tag wwft ON wwf.id = wwft.wake_word_file_id
        LEFT JOIN tagging.wake_word_file_designation wwfd ON wwf.id = wwfd.wake_word_file_id AND wwft.tag_id = wwfd.tag_id
WHERE
    wwfd.id IS NULL
ORDER BY
    ww.name,
    wwft.wake_word_file_id,
    wwft.tag_id,
    wwft.tag_value_id
