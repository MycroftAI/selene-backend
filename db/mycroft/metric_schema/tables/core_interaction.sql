CREATE TABLE metric.core_interaction (
    id                          uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    device_id                   uuid        NOT NULL
            REFERENCES device.device,
    core_id                     text        NOT NULL,
    start_ts                    TIMESTAMP   NOT NULL,
    stt_engine                  text,
    stt_transcription           text,
    stt_duration                NUMERIC,
    intent_type                 text,
    intent_duration             NUMERIC,
    fallback_handler_duration   NUMERIC,
    skill_handler               text,
    skill_duration              NUMERIC,
    tts_engine                  text,
    tts_utterance               text,
    tts_duration                NUMERIC,
    speech_playback_duration    NUMERIC,
    insert_ts                   TIMESTAMP   NOT NULL
            DEFAULT current_timestamp,
    UNIQUE (device_id, core_id)
)
