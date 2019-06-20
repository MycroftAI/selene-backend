from datetime import datetime
from selene.data.device import ManifestSkill, DeviceSkillRepository


def add_skill_to_manifest(db, device_id, skill):
    manifest_skill = ManifestSkill(
        device_id=device_id,
        install_method='test_install_method',
        install_status='test_install_status',
        skill_gid=skill.skill_gid,
        install_ts=datetime.utcnow(),
        update_ts=datetime.utcnow()
    )
    device_skill_repo = DeviceSkillRepository(db)
    manifest_skill.id = device_skill_repo.add_manifest_skill(
        skill.id,
        manifest_skill
    )

    return manifest_skill


def remove_manifest_skill(db, manifest_skill):
    device_skill_repo = DeviceSkillRepository(db)
    device_skill_repo.remove_manifest_skill(manifest_skill)
