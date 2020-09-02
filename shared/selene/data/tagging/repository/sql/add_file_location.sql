INSERT INTO
    tagging.file_location (server, directory)
VALUES
    (%(server)s, %(directory)s)
RETURNING
    id
