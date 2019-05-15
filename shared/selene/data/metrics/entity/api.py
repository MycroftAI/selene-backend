from dataclasses import dataclass
from datetime import datetime


@dataclass
class ApiMetric(object):
    url: str
    access_ts: datetime
    api: str
    duration: int
    http_status: int
    id: str = None
    account_id: str = None
    device_id: str = None
