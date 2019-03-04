CREATE TABLE skill.skill (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text        NOT NULL,
    url         text,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
