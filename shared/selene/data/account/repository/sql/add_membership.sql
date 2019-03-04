INSERT INTO
    account.membership (type, rate, rate_period)
VALUES
    (%(membership_type)s, %(rate)s, %(rate_period)s)
RETURNING
    id
