from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkillSetting(object):
    settings_definition: dict
    settings_values: dict
    device_names: List[str]


@dataclass
class DeviceSkillSetting(object):
    settings_display: dict
    settings_values: dict
    skill_id: str


@dataclass
class SettingsDisplay(object):
    skill_id: str
    display_data: dict
    id: str = None
