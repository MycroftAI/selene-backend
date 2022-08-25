DELETE FROM
    metric.stt_transcription
WHERE
    insert_ts::date = %(transcription_date)s
