from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkill(object):
    skill_id: str
    skill_name: str
    devices: List[str]
    display_name: str = None
    settings_version: str = None
    settings_display: dict = None
    settings: dict = None
