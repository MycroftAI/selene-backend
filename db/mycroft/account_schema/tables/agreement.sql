CREATE TABLE account.agreement (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement       text NOT NULL,
    version         text NOT NULL,
    effective_dt    date NOT NULL,
    content         oid  NOT NULL,
    UNIQUE (agreement, version)
);
