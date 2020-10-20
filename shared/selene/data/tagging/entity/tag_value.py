from dataclasses import dataclass


@dataclass
class TagValue:
    value: str
    display: str
    id: str = None
