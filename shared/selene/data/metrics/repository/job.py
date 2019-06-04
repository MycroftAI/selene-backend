from dataclasses import asdict

from ...repository_base import RepositoryBase
from ..entity.job import JobMetric


class JobRepository(RepositoryBase):
    def __init__(self, db):
        super(JobRepository, self).__init__(db, __file__)

    def add(self, job: JobMetric):
        db_request = self._build_db_request(
            sql_file_name='add_job_metric.sql',
            args=asdict(job)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result.id
