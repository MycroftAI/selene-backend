INSERT INTO
    skill.skill (skill_gid, family_name)
VALUES
    (%(skill_gid)s, %(family_name)s)
RETURNING
    id
