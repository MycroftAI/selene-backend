INSERT INTO
    skill.settings_display (skill_id, settings_display)
VALUES
    (%(skill_id)s, %(settings_display)s)
ON CONFLICT
    (skill_id)
DO UPDATE SET
    settings_display = %(settings_display)s
RETURNING
    id
