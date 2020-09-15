SELECT
    ww.name AS wake_word_name,
    ww.engine,
    wwf.name AS file_name,
    wwf.origin,
    wwf.submission_date,
    wwf.account_id,
    fl.directory,
    fl.server
FROM
    tagging.wake_word_file wwf
    INNER JOIN tagging.file_location fl ON fl.id = wwf.file_location_id
    INNER JOIN wake_word.wake_word ww on ww.id = wwf.wake_word_id
WHERE
    wwf.submission_date = %(submission_date)s
