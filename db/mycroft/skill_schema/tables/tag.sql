CREATE TABLE skill.tag (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid NOT NULL REFERENCES skill.skill,
    tag         text NOT NULL,
    UNIQUE (skill_id, tag)
);
