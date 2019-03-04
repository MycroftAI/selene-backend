CREATE TABLE account.account_membership (
    id                      uuid                    PRIMARY KEY
            DEFAULT gen_random_uuid(),
    account_id              uuid                    NOT NULL
            REFERENCES account.account ON DELETE CASCADE,
    membership_id           uuid                    NOT NULL
            REFERENCES account.membership,
    membership_ts_range     tsrange                 NOT NULL,
    payment_method          payment_method_enum     NOT NULL,
    payment_account_id      text                    NOT NULL,
    insert_ts               TIMESTAMP               NOT NULL
            DEFAULT CURRENT_TIMESTAMP,
    EXCLUDE USING gist (account_id WITH =, membership_ts_range with &&),
    UNIQUE (account_id, membership_id, membership_ts_range)
)
