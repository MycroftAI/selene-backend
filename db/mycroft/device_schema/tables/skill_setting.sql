CREATE TABLE device.skill_setting (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    device_skill_id uuid NOT NULL REFERENCES device.device_skill ON DELETE CASCADE,
    setting_id      uuid NOT NULL REFERENCES skill.setting,
    value           text NOT NULL,
    UNIQUE (device_skill_id, setting_id)
);
