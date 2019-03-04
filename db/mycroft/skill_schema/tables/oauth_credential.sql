CREATE TABLE skill.oauth_credential (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    developer_id        uuid        NOT NULL REFERENCES account.account,
    application_name    text        NOT NULL,
    oauth_client_id     text        NOT NULL,
    oauth_client_secret text        NOT NULL,
    oauth_scope         text        NOT NULL,
    token_uri           text        NOT NULL,
    auth_uri            text        NOT NULL,
    revoke_uri          text        NOT NULL,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (developer_id, application_name)
)
