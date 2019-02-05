from dataclasses import dataclass
from typing import List


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    id: str
    email_address: str
    password: str
    refresh_tokens: List[str]
