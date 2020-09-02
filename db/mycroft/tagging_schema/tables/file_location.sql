-- Servers and directories of files used for training machine learning models.
CREATE TABLE tagging.file_location (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    server          inet        NOT NULL,
    directory       text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (server, directory)
);
