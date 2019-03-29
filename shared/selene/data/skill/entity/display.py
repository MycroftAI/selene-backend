from dataclasses import dataclass


@dataclass
class SkillDisplay(object):
    skill_id: str
    core_version: str
    display_data: dict
    id: str = None
