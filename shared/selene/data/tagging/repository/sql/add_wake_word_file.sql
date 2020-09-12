INSERT INTO
    tagging.wake_word_file (
        wake_word_id,
        name,
        origin,
        submission_date,
        account_id,
        file_location_id
    )
VALUES
    (
        %(wake_word_id)s,
        %(file_name)s,
        %(origin)s,
        %(submission_date)s,
        %(account_id)s,
        %(file_location_id)s
    )
