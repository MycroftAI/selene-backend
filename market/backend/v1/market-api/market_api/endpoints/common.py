from dataclasses import dataclass, field
from typing import List

from markdown import markdown

DEFAULT_ICON_COLOR = '#6C7A89'
DEFAULT_ICON_NAME = 'comment-alt'
SYSTEM_CATEGORY = 'System'
UNDEFINED_CATEGORY = 'Not Categorized'
VALID_INSTALLATION_VALUES = ('failed', 'installed', 'installing', 'uninstalled')


@dataclass
class RepositorySkill(object):
    """Represents a single skill defined in the Mycroft Skills repository."""
    branch: str
    categories: List[str]
    created: str
    credits: List[dict]
    description: str
    icon: dict
    id: str
    is_mycroft_made: bool = field(init=False)
    is_system_skill: bool = field(init=False)
    last_update: str
    market_category: str = field(init=False)
    platforms: List[str]
    repository_owner: str
    repository_url: str
    skill_name: str
    summary: str
    tags: List[str]
    title: str
    triggers: List[str]
    icon_image: str = field(default=None)

    def __post_init__(self):
        self.is_system_skill = False
        if 'system' in self.tags:
            self.is_system_skill = True
            self.market_category = SYSTEM_CATEGORY
        elif self.categories:
            # a skill may have many categories.  the first one in the
            # list is considered the "primary" category.  This is the
            # category the marketplace will use to group the skill.
            self.market_category = self.categories[0]
        else:
            self.market_category = UNDEFINED_CATEGORY

        if not self.icon:
            self.icon = dict(icon=DEFAULT_ICON_NAME, color=DEFAULT_ICON_COLOR)

        self.is_mycroft_made = self.credits[0].get('name') == 'Mycroft AI'
        self.summary = markdown(self.summary, output_format='html5')
