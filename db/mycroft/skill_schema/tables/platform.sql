CREATE TABLE skill.platform (
    id          uuid  PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id    uuid  NOT NULL REFERENCES skill.skill,
    platform    text  NOT NULL,
    UNIQUE (skill_id, platform)
);
