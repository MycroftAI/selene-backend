from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkillSetting(object):
    settings_definition: dict
    settings_values: dict
    devices: List[str]
