from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class ApiMetric(object):
    url: str
    access_ts: datetime
    api: str
    duration: Decimal
    http_status: int
    id: str = None
    account_id: str = None
    device_id: str = None
