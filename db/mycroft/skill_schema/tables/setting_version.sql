CREATE TABLE skill.setting_version (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id uuid NOT NULL REFERENCES skill.skill,
    version_hash text NOT NULL,
    UNIQUE (skill_id, version_hash)
)