CREATE TABLE account.agreement (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement       agreement_enum  NOT NULL,
    version         text            NOT NULL,
    effective_dt    date            NOT NULL,
    content_id      oid             NOT NULL,
    UNIQUE (agreement, version)
);
