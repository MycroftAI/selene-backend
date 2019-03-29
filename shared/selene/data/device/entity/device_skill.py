from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceSkill(object):
    id: str
    device_name: str
    install_method: str
    install_status: str
    skill_id: str
    install_failure_reason: str = None
    install_ts: datetime = None
