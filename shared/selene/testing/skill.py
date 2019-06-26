from selene.data.skill import (
    SettingsDisplay,
    SettingsDisplayRepository,
    Skill,
    SkillRepository
)


def build_text_field():
    return dict(
        name='textfield',
        type='text',
        label='Text Field',
        placeholder='Text Placeholder'
    )


def build_label_field():
    return dict(
        type='label',
        label='This is a section label.'
    )


def _build_display_data(skill_gid, fields):
    gid_parts = skill_gid.split('|')
    if len(gid_parts) == 3:
        skill_name = gid_parts[1]

    else:
        skill_name = gid_parts[0]
    skill_identifier = skill_name + '-123456'
    settings_display = dict(
        skill_gid=skill_gid,
        identifier=skill_identifier,
        display_name=skill_name,
    )
    if fields is not None:
        settings_display.update(
            skillMetadata=dict(
                sections=[dict(name='Section Name', fields=fields)]
            )
        )

    return settings_display


def add_skill(db, skill_global_id, settings_fields=None):
    display_data = _build_display_data(skill_global_id, settings_fields)
    skill_repo = SkillRepository(db)
    skill_id = skill_repo.ensure_skill_exists(skill_global_id)
    skill = Skill(skill_global_id, skill_id)
    settings_display = SettingsDisplay(skill_id, display_data)
    settings_display_repo = SettingsDisplayRepository(db)
    settings_display.id = settings_display_repo.add(settings_display)

    return skill, settings_display


def remove_skill(db, skill):
    skill_repo = SkillRepository(db)
    skill_repo.remove_by_gid(skill_gid=skill.skill_gid)
