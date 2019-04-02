from os import path
from typing import List

from selene.util.db import (
    Cursor,
    DatabaseRequest,
    DatabaseBatchRequest,
    get_sql_from_file
)


class RepositoryBase(object):
    def __init__(self, db, repository_path):
        self.cursor = Cursor(db)
        self.sql_dir = path.join(path.dirname(repository_path), 'sql')

    def _build_db_request(self, sql_file_name: str, args: dict = None):
        return DatabaseRequest(
            sql=get_sql_from_file(path.join(self.sql_dir, sql_file_name)),
            args=args
        )

    def _build_db_batch_request(self, sql_file_name: str, args: List[dict]):
        return DatabaseBatchRequest(
            sql=get_sql_from_file(path.join(self.sql_dir, sql_file_name)),
            args=args
        )

    def _select_one_into_dataclass(self, dataclass, sql_file_name, args=None):
        db_request = self._build_db_request(sql_file_name, args)
        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            return_value = None
        else:
            return_value = dataclass(**db_result)

        return return_value

    def _select_all_into_dataclass(self, dataclass, sql_file_name, args=None):
        db_request = self._build_db_request(sql_file_name, args)
        db_result = self.cursor.select_all(db_request)

        return [dataclass(**row) for row in db_result]
