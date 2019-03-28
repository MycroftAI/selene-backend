CREATE TABLE skill.skill (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    global_id   text        NOT NULL UNIQUE,
    name        text        NOT NULL,
    insert_ts   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
