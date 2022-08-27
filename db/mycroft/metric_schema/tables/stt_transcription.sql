-- The metrics stored on this table provide the ability to reconcile STT transcription activity with a
-- bill from a service provider.  It can also be used to derive performance metrics by service provider.
-- To keep our promise of privacy, this data will only be available at the account level for 24 hours, at
-- which point it will be aggregated and wiped.
CREATE TABLE metric.stt_transcription (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id              uuid        NOT NULL,
    engine                  TEXT        NOT NULL,
    success                 BOOLEAN     NOT NULL,
    audio_duration          INTEGER     NOT NULL DEFAULT 0,
    transcription_duration  INTEGER     NOT NULL DEFAULT 0,
    insert_ts               TIMESTAMP   NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS
    stt_transcription_account_activity_idx
ON
    metric.stt_transcription (account_id, insert_ts)
;
