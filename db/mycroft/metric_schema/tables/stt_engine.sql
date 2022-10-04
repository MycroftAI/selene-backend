CREATE TABLE metric.stt_engine (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_dt             DATE        NOT NULL DEFAULT current_date,
    engine                  TEXT        NOT NULL,
    requests                INTEGER     NOT NULL DEFAULT 0,
    success_rate            NUMERIC     NOT NULL,
    transcription_speed     NUMERIC     NOT NULL,
    audio_duration          NUMERIC     NOT NULL DEFAULT 0,
    transcription_duration  NUMERIC     NOT NULL DEFAULT 0,
    insert_ts               TIMESTAMP   NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS
    stt_transcription_engine_activity_idx
ON
    metric.stt_engine (activity_dt, engine)
;
