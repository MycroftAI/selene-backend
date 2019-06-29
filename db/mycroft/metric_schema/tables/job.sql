CREATE TABLE metric.job (
    id          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    job_name    text        NOT NULL,
    batch_date  date        NOT NULL,
    start_ts    TIMESTAMP   NOT NULL,
    end_ts      TIMESTAMP   NOT NULL,
    command     text        NOT NULL,
    success     BOOLEAN     NOT NULL,
    UNIQUE (job_name, start_ts)
)
