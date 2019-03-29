SELECT
    id,
    skill_id,
    core_version,
    display_data
FROM
    skill.display
WHERE
    id = %(skill_display_id)s
