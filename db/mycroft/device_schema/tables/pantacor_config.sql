CREATE TABLE device.pantacor_config (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id       uuid        UNIQUE REFERENCES device.device ON DELETE CASCADE,
    pantacor_id     text        UNIQUE NOT NULL,
    ssh_public_key  text,
    auto_update     bool        NOT NULL DEFAULT false,
    release         text        NOT NULL DEFAULT 'stable',
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
