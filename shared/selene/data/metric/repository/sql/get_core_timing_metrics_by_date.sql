SELECT
    device_id,
    metric_type,
    metric_value
FROM
    metric.core
WHERE
    metric_type = 'timing'
    AND metric_value ->> 'id' NOT IN ('unknown', 'null')
    AND insert_ts::date = %(metric_date)s
ORDER BY
    metric_value ->> 'id',
    metric_value ->> 'start_time'
