SELECT
    id
FROM
    tagging.file_location
WHERE
    server = %(server)s
    AND directory = %(directory)s
