CREATE TABLE skill.display (
    id              uuid                PRIMARY KEY
            DEFAULT gen_random_uuid(),
    skill_id        uuid                NOT NULL
            REFERENCES skill.skill,
    core_version    core_version_enum   NOT NULL,
    display_data    json                NOT NULL,
    insert_ts       TIMESTAMP           NOT NULL
            DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, core_version)
);
