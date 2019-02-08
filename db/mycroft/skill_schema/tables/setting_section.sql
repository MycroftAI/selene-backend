CREATE TABLE skill.setting_section (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_version_id    uuid    NOT NULL REFERENCES skill.setting_version,
    section             text    NOT NULL,
    description         text,
    display_order       integer NOT NULL,
    UNIQUE (skill_version_id, section)
);
