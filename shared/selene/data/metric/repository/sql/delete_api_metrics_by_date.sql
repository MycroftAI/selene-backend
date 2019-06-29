DELETE FROM
    metric.api
WHERE
    access_ts::date = %(delete_date)s
