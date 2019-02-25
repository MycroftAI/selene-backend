INSERT INTO
    device.account_preferences(
        account_id,
        date_format,
        time_format,
        measurement_system,
        wake_word_id,
        text_to_speech_id
      )
VALUES
    (
        %(account_id)s,
        %(date_format)s,
        %(time_format)s,
        %(measurement_system)s,
        %(wake_word_id)s,
        %(text_to_speech_id)s
    )