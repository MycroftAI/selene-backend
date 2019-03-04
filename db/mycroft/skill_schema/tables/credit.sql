CREATE TABLE skill.credit (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid        NOT NULL REFERENCES skill.skill,
    github_id   text        NOT NULL,
    github_name text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, github_id)
);
