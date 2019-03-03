CREATE TABLE skill.settings_display (
    id                  uuid        PRIMARY KEY
            DEFAULT gen_random_uuid(),
    skill_id            uuid        NOT NULL
            REFERENCES skill.skill ON DELETE CASCADE,
    settings_display    jsonb       NOT NULL,
    hash                text        NOT NULL,
    insert_ts           TIMESTAMP   NOT NULL
        DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, settings_display)
);
