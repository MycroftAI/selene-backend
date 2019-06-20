from dataclasses import dataclass
from datetime import datetime


@dataclass
class CoreMetric(object):
    device_id: str
    metric_type: str
    insert_ts: datetime
    metric_value: dict
    id: str = None
