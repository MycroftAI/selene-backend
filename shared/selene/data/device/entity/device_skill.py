from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceSkill(object):
    id: str
    device_id: str
    install_method: str
    install_status: str
    skill_id: str
    skill_gid: str
    device_name: str = None
    install_failure_reason: str = None
    install_ts: datetime = None
    update_ts: datetime = None
    skill_settings: dict = None
    skill_settings_display_id: str = None


@dataclass
class ManifestSkill(object):
    device_id: str
    install_method: str
    install_status: str
    skill_gid: str
    install_failure_reason: str = None
    install_ts: datetime = None
    update_ts: datetime = None
    id: str = None
