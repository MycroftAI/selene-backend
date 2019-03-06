from dataclasses import dataclass


@dataclass
class Geography(object):
    country: str
    postal_code: str
    time_zone: str
    id: str = None
