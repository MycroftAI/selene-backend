from dataclasses import dataclass


@dataclass
class Region(object):
    id: str
    region_code: str
    name: str
