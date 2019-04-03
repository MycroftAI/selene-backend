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
ON CONFLICT
    (account_id)
DO UPDATE SET
    date_format = %(date_format)s,
    time_format = %(time_format)s,
    measurement_system = %(measurement_system)s
RETURNING
    id
