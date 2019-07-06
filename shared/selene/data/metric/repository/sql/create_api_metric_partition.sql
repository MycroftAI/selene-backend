CREATE TABLE IF NOT EXISTS
    metric.api_history_{partition}
PARTITION OF
    metric  .api_history
FOR VALUES FROM
    (%(start_ts)s) TO (%(end_ts)s)
