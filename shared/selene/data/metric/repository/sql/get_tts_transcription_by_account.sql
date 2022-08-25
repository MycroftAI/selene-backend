SELECT
    account_id,
    engine,
    success,
    audio_duration,
    transcription_duration
FROM
    metric.stt_transcription
WHERE
    account_id = %(account_id)s
