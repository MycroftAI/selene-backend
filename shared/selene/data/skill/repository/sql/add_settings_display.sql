INSERT INTO
    skill.settings_display (skill_id, settings_display)
VALUES
    (%(skill_id)s, %(settings_display)s)
RETURNING
    id