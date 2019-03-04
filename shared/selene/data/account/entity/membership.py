from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Membership(object):
    type: str
    rate: Decimal
    rate_period: str
    id: str = None
