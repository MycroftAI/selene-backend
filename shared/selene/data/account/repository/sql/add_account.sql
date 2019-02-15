INSERT INTO
    account.account (email_address, password, display_name)
VALUES
    (%(email_address)s, %(password)s, %(display_name)s)
RETURNING
    id
