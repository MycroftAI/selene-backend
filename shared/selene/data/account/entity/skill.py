from dataclasses import dataclass
from typing import List


@dataclass
class AccountSkill(object):
    skill_name: str
    devices: List[str]
    settings_version: str = None
    settings_meta: dict = None
    settings: dict = None
