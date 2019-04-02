CREATE TABLE skill.skill (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_gid   text        NOT NULL UNIQUE,
    family_name text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
