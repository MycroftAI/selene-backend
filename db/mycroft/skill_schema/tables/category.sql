CREATE TABLE skill.category (
    id          uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid            NOT NULL REFERENCES skill.skill,
    category    category_enum   NOT NULL,
    insert_ts   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (skill_id, category)
);
