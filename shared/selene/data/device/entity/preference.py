from dataclasses import dataclass


@dataclass
class AccountPreferences(object):
    date_format: str
    time_format: str
    measurement_system: str
    id: str = None
