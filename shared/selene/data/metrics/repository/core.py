import json
from dataclasses import asdict

from ..entity.core import CoreMetric
from ...repository_base import RepositoryBase


class CoreMetricRepository(RepositoryBase):
    def __init__(self, db):
        super(CoreMetricRepository, self).__init__(db, __file__)

    def add(self, metric: CoreMetric):
        db_request_args = asdict(metric)
        db_request_args['metric_value'] = json.dumps(db_request_args['metric_value'])
        db_request = self._build_db_request(
            sql_file_name='add_core_metric.sql',
            args=db_request_args
        )
        self.cursor.insert(db_request)

    def get_metrics_by_device(self, device_id):
        return self._select_all_into_dataclass(
            CoreMetric,
            sql_file_name='get_core_metric_by_device.sql',
            args=dict(device_id=device_id)
        )
