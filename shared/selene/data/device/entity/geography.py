from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Geography(object):
    country: str
    region: str
    city: str
    time_zone: str
    latitude: Decimal = None
    longitude: Decimal = None
    id: str = None
