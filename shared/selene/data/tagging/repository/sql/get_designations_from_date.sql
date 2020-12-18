SELECT
    wwf.id AS file_id,
    wwf.name AS file_name,
    fl.directory AS file_directory,
    wwfd.tag_id,
    wwfd.tag_value_id
FROM
    tagging.wake_word_file_designation wwfd
    INNER JOIN tagging.wake_word_file wwf ON wwf.id = wwfd.wake_word_file_id
    INNER JOIN tagging.file_location fl on fl.id = wwf.file_location_id
WHERE
    wwfd.insert_ts::date >= %(start_date)s
