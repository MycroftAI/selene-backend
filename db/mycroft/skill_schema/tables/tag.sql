CREATE TABLE skill.tag (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid        NOT NULL REFERENCES skill.skill,
    tag         text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, tag)
);
