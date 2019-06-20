from selene.data.skill import Skill, SkillRepository


def add_skill(db, skill_global_id):
    skill_repo = SkillRepository(db)
    skill_id = skill_repo.ensure_skill_exists(skill_global_id=skill_global_id)

    return Skill(skill_global_id, skill_id)


def remove_skill(db, skill_global_id):
    skill_repo = SkillRepository(db)
    skill_repo.remove_by_gid(skill_gid=skill_global_id)
