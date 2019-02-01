from dataclasses import dataclass


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    id: str
    email_address: str
    refresh_token: str
