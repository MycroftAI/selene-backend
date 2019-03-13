CREATE TABLE skill.display (
    id              uuid                PRIMARY KEY
            DEFAULT gen_random_uuid(),
    skill_name      text                NOT NULL,
    core_version    core_version_enum   NOT NULL,
    display_data    json                NOT NULL,
    insert_ts       TIMESTAMP           NOT NULL
            DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_name, core_version)
);
