SELECT
    id,
    skill_id,
    core_version,
    display_data
FROM
    skill.display
WHERE
    core_version = %(core_version)s
