INSERT INTO
    metric.stt_transcription
VALUES (
    DEFAULT,
    %(account_id)s,
    %(engine)s,
    %(success)s,
    %(audio_duration)s,
    %(transcription_duration)s
)
RETURNING
    id
