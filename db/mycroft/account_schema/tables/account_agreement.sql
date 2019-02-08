CREATE TABLE account.account_agreement (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid    NOT NULL REFERENCES account.account ON DELETE CASCADE,
    agreement_id        uuid    NOT NULL REFERENCES account.agreement,
    agreement_ts_range  tsrange NOT NULL,
    EXCLUDE USING gist (account_id WITH =, agreement_ts_range with &&),
    UNIQUE (account_id, agreement_id, agreement_ts_range)
);
