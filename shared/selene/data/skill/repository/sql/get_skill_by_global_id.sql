SELECT
    id,
    global_id,
    name
FROM
    skill.skill
WHERE
    global_id = %(global_id)s;
