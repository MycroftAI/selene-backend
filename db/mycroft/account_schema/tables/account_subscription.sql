CREATE TABLE account.account_subscription (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id              uuid        NOT NULL REFERENCES account.account ON DELETE CASCADE,
    subscription_id         uuid        NOT NULL REFERENCES account.subscription,
    subscription_ts_range   tsrange     NOT NULL,
    stripe_customer_id      text        NOT NULL,
    insert_ts               TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    EXCLUDE USING gist (account_id WITH =, subscription_ts_range with &&),
    UNIQUE (account_id, subscription_id, subscription_ts_range)
)
