from dataclasses import dataclass
from typing import List

from .tag_value import TagValue


@dataclass
class Tag:
    id: str
    name: str
    title: str
    instructions: str
    values: List[TagValue]
