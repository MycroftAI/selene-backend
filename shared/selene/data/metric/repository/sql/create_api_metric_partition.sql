CREATE TABLE IF NOT EXISTS
    metric.api_history_{partition}
PARTITION OF
    metrics.api_history
FOR VALUES FROM
    (%(start_ts)s) TO (%(end_ts)s)
