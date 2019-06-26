from dataclasses import dataclass
from typing import List


@dataclass
class SkillVersion(object):
    version: str
    display_name: str


@dataclass
class Skill(object):
    skill_gid: str
    id: str = None


@dataclass
class SkillFamily(object):
    display_name: str
    family_name: str
    has_settings: bool
    market_id: str
    skill_ids: List[str]
