INSERT INTO
    skill.settings_display (skill_id, settings_display)
VALUES
    (%(skill_id)s, %(display_data)s)
RETURNING
    id
