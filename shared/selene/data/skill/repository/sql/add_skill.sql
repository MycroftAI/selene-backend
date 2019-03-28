INSERT INTO
    skill.skill (global_id, name)
VALUES
    (%(global_id)s, %(skill_name)s)
RETURNING
    id
