INSERT INTO
    account.account (email_address, password)
VALUES
    (%(email_address)s, %(password)s)
RETURNING
    id
