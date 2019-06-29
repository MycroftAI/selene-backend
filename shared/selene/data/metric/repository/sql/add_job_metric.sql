INSERT INTO
    metric.job
VALUES (
    DEFAULT,
    %(job_name)s,
    %(batch_date)s,
    %(start_ts)s,
    %(end_ts)s,
    %(command)s,
    %(success)s
)
RETURNING
    id
