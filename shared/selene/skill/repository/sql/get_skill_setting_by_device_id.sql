SELECT
    json_build_object(
        'uuid', skill.id,
        'name', skill.name,
        'identifier', ver.version_hash,
        'skillMetadata', json_build_object(
            'sections', (
                select json_agg(json_build_object(
                    'uuid', sec.id,
                    'section', sec.section,
                    'display', sec.display_order,
                    'fields', (
                        select json_agg(json_build_object(
                            'name', setting.setting,
                            'type', setting.setting_type,
                            'label', setting.label,
                            'hint', setting.hint,
                            'placeholder', setting.placeholder,
                            'hide', setting.hidden,
                            'value', (select value from device.skill_setting where device_skill_id = dev_skill.id and setting_id = setting.id),
                            'options', setting.options,
                            'order', setting.display_order
                        ))
                        FROM
                            skill.setting setting
                        WHERE
                            setting.setting_section_id = sec.id
                    )
                ))
                FROM
                    skill.setting_section sec
                WHERE
                    sec.skill_version_id = ver.id
        ))
    ) as skill
FROM
    device.device dev
INNER JOIN
    device.device_skill dev_skill ON dev.id = dev_skill.device_id
INNER JOIN
    skill.skill skill ON dev_skill.skill_id = skill.id
INNER JOIN
    skill.setting_version ver ON skill.id = ver.skill_id
WHERE
    dev.id = %(device_id)s;

