"""CRUD operations for the metrics.api and metrics.api_history tables.

The metrics.api table contains performance metrics for the Selene APIs.  There
are millions of API requests made per day.  This can lead to poor performance
querying the table after only a few days.  This problem is solved by
partitioning the table into smaller daily tables.

The declarative partitioning scheme provided by Postgres is used to create
the partitions of the metrics.api_history table
"""
import os
from dataclasses import asdict
from datetime import date, datetime, time

from ..entity.api import ApiMetric
from ...repository_base import RepositoryBase

DUMP_FILE_DIR = '/opt/selene/dump'


class ApiMetricsRepository(RepositoryBase):
    def __init__(self, db):
        super(ApiMetricsRepository, self).__init__(db, __file__)

    def add(self, metric: ApiMetric):
        db_request = self._build_db_request(
            sql_file_name='add_api_metric.sql',
            args=asdict(metric)
        )
        self.cursor.insert(db_request)

    def create_partition(self, partition_date: date):
        """Create a daily partition for the metrics.api_history table."""
        start_ts = datetime.combine(partition_date, time.min)
        end_ts = datetime.combine(partition_date, time.max)
        db_request = self._build_db_request(
            sql_file_name='create_api_metric_partition.sql',
            args=dict(start_ts=str(start_ts), end_ts=str(end_ts)),
            sql_vars=dict(partition=partition_date.strftime('%Y%m%d'))
        )
        self.cursor.execute(db_request)

        db_request = self._build_db_request(
            sql_file_name='create_api_metric_partition_index.sql',
            sql_vars=dict(partition=partition_date.strftime('%Y%m%d'))
        )
        self.cursor.execute(db_request)

    def copy_to_partition(self, partition_date: date):
        """Copy rows from metrics.api table to metrics.api_history."""
        dump_file_name = 'api_metrics_' + str(partition_date)
        dump_file_path = os.path.join(DUMP_FILE_DIR, dump_file_name)
        db_request = self._build_db_request(
            sql_file_name='get_api_metrics_for_date.sql',
            args=dict(metrics_date=partition_date)
        )
        table_name = 'metrics.api_history_' + partition_date.strftime('%Y%m%d')
        self.cursor.dump_query_result_to_file(db_request, dump_file_path)
        self.cursor.load_dump_file_to_table(table_name, dump_file_path)
        os.remove(dump_file_path)

    def remove_by_date(self, partition_date: date):
        """Delete from metrics.api table after copying to metrics.api_history"""
        db_request = self._build_db_request(
            sql_file_name='delete_api_metrics_by_date.sql',
            args=dict(delete_date=partition_date)
        )
        self.cursor.delete(db_request)
