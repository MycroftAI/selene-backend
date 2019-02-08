CREATE TABLE skill.setting (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_section_id  uuid    NOT NULL REFERENCES skill.setting_section,
    setting             text    NOT NULL,
    setting_type        text    NOT NULL,
    hint                text,
    label               text,
    placeholder         text,
    options             text,
    default_value       text,
    hidden              boolean NOT NULL,
    display_order       integer NOT NULL,
    UNIQUE (setting_section_id, setting)
);
