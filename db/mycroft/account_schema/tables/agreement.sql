CREATE TABLE account.agreement (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement       agreement_enum  NOT NULL,
    version         text            NOT NULL,
    effective       daterange       NOT NULL,
    content_id      oid             NOT NULL,
    EXCLUDE USING gist (agreement WITH =, effective WITH &&),
    UNIQUE (agreement, version)
);
