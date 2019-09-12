SELECT
    sd.id,
    sd.skill_id,
    sd.settings_display as display_data
FROM
    skill.settings_display sd
    INNER JOIN skill.skill s ON sd.skill_id = s.id
WHERE
    s.skill_gid = %(global_id)s
