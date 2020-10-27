SELECT
    json_build_object(
        'name', ww.name,
        'engine', ww.engine,
        'id', ww.id
    ) AS wake_word,
    wwf.name,
    wwf.origin,
    wwf.submission_date,
    wwf.account_id,
    wwf.status,
    wwf.id,
    json_build_object(
        'server', fl.server,
        'directory', fl.directory,
        'id', ww.id
    ) AS location
FROM
    tagging.wake_word_file wwf
    INNER JOIN tagging.file_location fl ON fl.id = wwf.file_location_id
    INNER JOIN wake_word.wake_word ww on ww.id = wwf.wake_word_id
WHERE
    {where_clause}
