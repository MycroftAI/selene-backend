CREATE INDEX IF NOT EXISTS
    api_history_{partition}_access_ts_idx
ON
    metric.api_history_{partition} (access_ts)
