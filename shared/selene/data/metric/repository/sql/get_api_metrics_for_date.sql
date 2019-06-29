SELECT
    *
FROM
    metric.api
WHERE
    access_ts::date = %(metrics_date)s
