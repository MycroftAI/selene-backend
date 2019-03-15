from dataclasses import dataclass


@dataclass
class City(object):
    id: str
    latitude: str
    longitude: str
    name: str
    timezone: str
