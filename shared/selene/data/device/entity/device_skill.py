from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ManifestSkill(object):
    device_id: str
    install_method: str
    install_status: str
    skill_gid: str
    install_failure_reason: str = None
    install_ts: datetime = None
    skill_id: str = None
    update_ts: datetime = None
    id: str = None


@dataclass
class AccountSkillSettings(object):
    install_method: str
    skill_id: str
    device_ids: List[str] = None
    settings_values: dict = None
    settings_display_id: str = None


@dataclass
class DeviceSkillSettings(object):
    skill_id: str
    skill_gid: str
    settings_values: dict = None
    settings_display_id: str = None
