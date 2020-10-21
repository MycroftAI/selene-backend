UPDATE
    tagging.wake_word_file
SET
    file_location_id = %(file_location_id)s,
    status = 'stored'::tagging_file_status_enum
WHERE
    id = %(wake_word_file_id)s
