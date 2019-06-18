from dataclasses import dataclass
from typing import List


@dataclass
class Setting(object):
    """Representation of a Skill setting"""
    id: str
    setting_section_id: str
    setting: str
    setting_type: str
    hidden: bool
    display_order: int
    hint: str = None
    label: str = None
    placeholder: str = None
    options: str = None
    default_value: str = None
    value: str = None


@dataclass
class SettingSection(object):
    """Representation of a section from a Skill Setting"""
    id: str
    skill_version_id: str
    section: str
    display_order: int
    description: str = None
    settings: List[Setting] = None


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
