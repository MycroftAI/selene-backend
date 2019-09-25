from dataclasses import dataclass


@dataclass
class City(object):
    id: str
    latitude: str
    longitude: str
    name: str
    timezone: str


@dataclass
class GeographicLocation(object):
    city: str
    country: str
    region: str
    latitude: str
    longitude: str
    timezone: str
