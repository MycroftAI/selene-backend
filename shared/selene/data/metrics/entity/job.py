from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class JobMetric(object):
    job_name: str
    batch_date: date
    start_ts: datetime
    end_ts: datetime
    command: str
    success: bool
    id: str = None
