CREATE TABLE skill.category (
    id          uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid            NOT NULL REFERENCES skill.skill,
    category    category_enum   NOT NULL,
    UNIQUE (skill_id, category)
);
