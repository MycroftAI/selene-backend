CREATE TABLE device.category (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id  uuid NOT NULL REFERENCES account.account ON DELETE CASCADE,
    category    text,
    UNIQUE (account_id, category)
);
