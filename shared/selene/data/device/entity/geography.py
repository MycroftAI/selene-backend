from dataclasses import dataclass


@dataclass
class Geography(object):
    country: str
    time_zone: str
    id: str = None
