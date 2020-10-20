from dataclasses import dataclass


@dataclass
class WakeWordFileTag:
    file_id: str
    session_id: str
    tag_id: str
    tag_value_id: str
    id: str = None
