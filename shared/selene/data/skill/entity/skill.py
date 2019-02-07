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
