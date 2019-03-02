from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkillSetting(object):
    settings_display: dict
    settings_values: dict
    devices: List[str]
