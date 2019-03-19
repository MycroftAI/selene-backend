INSERT INTO
    device.account_preferences(
        account_id,
        date_format,
        time_format,
        measurement_system
      )
VALUES
    (
        %(account_id)s,
        %(date_format)s,
        %(time_format)s,
        %(measurement_system)s
    )
