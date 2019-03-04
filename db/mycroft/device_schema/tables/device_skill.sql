CREATE TABLE device.device_skill (
    id                      uuid        PRIMARY KEY
        DEFAULT gen_random_uuid(),
    device_id               uuid        NOT NULL
        REFERENCES device.device
        ON DELETE CASCADE,
    skill_id                uuid        NOT NULL
        REFERENCES skill.skill,
    install_method          text	    NOT NULL
        DEFAULT 'msm',
    install_status          text	    NOT NULL
        DEFAULT 'installed',
    install_failure_reason  text,
    install_ts              TIMESTAMP,
    update_ts               TIMESTAMP,
    skill_settings_display_id   uuid
        REFERENCES skill.settings_display,
    settings                json,
    insert_ts               TIMESTAMP   NOT NULL
        DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (device_id, skill_id)
);
