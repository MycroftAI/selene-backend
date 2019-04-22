from dataclasses import asdict

from ..entity.api import ApiMetric
from ...repository_base import RepositoryBase


class ApiMetricsRepository(RepositoryBase):
    def __init__(self, db):
        super(ApiMetricsRepository, self).__init__(db, __file__)

    def add(self, metric: ApiMetric):
        db_request = self._build_db_request(
            sql_file_name='add_api_metric.sql',
            args=asdict(metric)
        )
        self.cursor.insert(db_request)
