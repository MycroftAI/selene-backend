CREATE TABLE skill.setting_meta (
    id              uuid        PRIMARY KEY
        DEFAULT gen_random_uuid(),
    skill_id        uuid        NOT NULL
        REFERENCES skill.skill
        ON DELETE CASCADE,
    version         text        NOT NULL,
    settings_meta   json        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL
        DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, version)
);
