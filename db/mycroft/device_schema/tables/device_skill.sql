CREATE TABLE device.device_skill (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id               uuid        NOT NULL REFERENCES device.device ON DELETE CASCADE,
    skill_id                uuid        NOT NULL REFERENCES skill.skill,
    install_method          text	NOT NULL DEFAULT 'msm',
    install_status          text	NOT NULL DEFAULT 'installed',
    install_failure_reason  text,
    install_ts              timestamp,
    update_ts               timestamp,
    beta                    boolean     NOT NULL DEFAULT FALSE,
    UNIQUE (device_id, skill_id)
);
