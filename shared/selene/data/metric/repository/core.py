import json
from dataclasses import asdict
from datetime import date
from typing import List
from ..entity.core import CoreMetric, CoreInteraction
from ...repository_base import RepositoryBase


class CoreMetricRepository(RepositoryBase):
    def __init__(self, db):
        super(CoreMetricRepository, self).__init__(db, __file__)

    def add(self, metric: CoreMetric):
        db_request_args = asdict(metric)
        db_request_args['metric_value'] = json.dumps(
            db_request_args['metric_value']
        )
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

    def get_metrics_by_date(self, metric_date: date) -> List[CoreMetric]:
        return self._select_all_into_dataclass(
            CoreMetric,
            sql_file_name='get_core_timing_metrics_by_date.sql',
            args=dict(metric_date=metric_date)
        )

    def add_interaction(self, interaction: CoreInteraction) -> str:
        db_request = self._build_db_request(
            sql_file_name='add_core_interaction.sql',
            args=asdict(interaction)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result.id
