CREATE TABLE skill.activation (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid        NOT NULL REFERENCES skill.skill,
    activation  text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, activation)
);
