from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Membership(object):
    type: str
    rate: Decimal
    rate_period: str
    stripe_plan: str
    id: str = None
