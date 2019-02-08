CREATE TABLE skill.oauth_token (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    oauth_credential_id uuid NOT NULL REFERENCES skill.oauth_credential,
    account_id          uuid NOT NULL REFERENCES account.account,
    token               json NOT NULL,
    UNIQUE (oauth_credential_id, account_id)
)