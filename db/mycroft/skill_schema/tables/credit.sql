CREATE TABLE skill.credit (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid NOT NULL REFERENCES skill.skill,
    github_id   text NOT NULL,
    github_name text NOT NULL,
    UNIQUE (skill_id, github_id)
);
