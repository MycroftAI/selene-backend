from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Geography(object):
    country: str
    region: str
    city: str
    time_zone: str
    latitude: Decimal
    longitude: Decimal
    id: str = None
