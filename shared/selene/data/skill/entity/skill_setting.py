from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkillSetting(object):
    skill_id: str
    settings_display: dict
    settings_values: dict
    devices: List[str]
