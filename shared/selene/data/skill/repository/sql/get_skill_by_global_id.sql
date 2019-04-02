SELECT
    id,
    skill_gid
FROM
    skill.skill
WHERE
    skill_gid = %(skill_gid)s;
