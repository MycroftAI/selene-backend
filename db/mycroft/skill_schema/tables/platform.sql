CREATE TABLE skill.platform (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid        NOT NULL REFERENCES skill.skill,
    platform    text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, platform)
);
