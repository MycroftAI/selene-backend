CREATE TABLE skill.branch (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            uuid        NOT NULL REFERENCES skill.skill,
    repository_name     text        NOT NULL,
    branch              text        NOT NULL,
    display_name        text,
    short_description   text,
    long_description    text,
    icon_name           text,
    icon_color          text,
    icon_image_url      text,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_name, branch)
);
