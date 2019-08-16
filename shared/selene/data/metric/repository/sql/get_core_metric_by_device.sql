SELECT
    id,
    device_id,
    metric_type,
    metric_value
FROM
    metric.core
WHERE
    device_id = %(device_id)s
