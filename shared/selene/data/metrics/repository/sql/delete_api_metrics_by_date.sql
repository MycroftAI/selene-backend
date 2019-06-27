DELETE FROM
    metrics.api
WHERE
    access_ts::date = %(delete_date)s
