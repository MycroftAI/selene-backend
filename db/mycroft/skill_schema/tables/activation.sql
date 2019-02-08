CREATE TABLE skill.activation (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid NOT NULL REFERENCES skill.skill,
    activation  text NOT NULL,
    UNIQUE (skill_id, activation)
);
