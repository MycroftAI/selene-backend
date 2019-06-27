SELECT
    *
FROM
    metrics.api
WHERE
    access_ts::date = %(metrics_date)s
