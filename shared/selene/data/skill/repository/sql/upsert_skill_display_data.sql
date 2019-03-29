INSERT INTO
    skill.display (skill_id, core_version, display_data)
VALUES
    (
        %(skill_id)s,
        %(core_version)s,
        %(display_data)s
    )
ON CONFLICT
    (skill_id, core_version)
    DO UPDATE SET
    display_data = %(display_data)s
RETURNING
    id
