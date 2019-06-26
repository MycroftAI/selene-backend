import json
from datetime import datetime

from selene.data.device import DeviceSkillRepository, ManifestSkill


def add_device_skill(db, device_id, skill):
    manifest_skill = ManifestSkill(
        device_id=device_id,
        install_method='test_install_method',
        install_status='test_install_status',
        skill_id=skill.id,
        skill_gid=skill.skill_gid,
        install_ts=datetime.utcnow(),
        update_ts=datetime.utcnow()
    )
    device_skill_repo = DeviceSkillRepository(db)
    manifest_skill.id = device_skill_repo.add_manifest_skill(manifest_skill)

    return manifest_skill


def add_device_skill_settings(db, device_id, settings_display, settings_values):
    device_skill_repo = DeviceSkillRepository(db)
    device_skill_repo.update_device_skill_settings(
        [device_id],
        settings_display,
        settings_values
    )


def remove_device_skill(db, manifest_skill):
    device_skill_repo = DeviceSkillRepository(db)
    device_skill_repo.remove_manifest_skill(manifest_skill)
