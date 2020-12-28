CREATE TABLE account.account_agreement (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid        NOT NULL REFERENCES account.account ON DELETE CASCADE,
    agreement_id        uuid        NOT NULL REFERENCES account.agreement,
    accept_date         DATE        NOT NULL,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (account_id, agreement_id, accept_date)
);
