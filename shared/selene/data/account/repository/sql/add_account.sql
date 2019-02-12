INSERT INTO
    account.account (email_address, password, username)
VALUES
    (%(email_address)s, %(password)s, %(username)s)
RETURNING
    id
