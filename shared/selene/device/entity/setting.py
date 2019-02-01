from dataclasses import dataclass


@dataclass
class AccountPreferences(object):
    id: str
    date_format: str
    time_format: str
    measurement_system: str
