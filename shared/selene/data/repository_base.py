from os import path
from selene.util.db import Cursor, DatabaseRequest, get_sql_from_file


class RepositoryBase(object):
    def __init__(self, db, repository_path):
        self.cursor = Cursor(db)
        self.sql_dir = path.join(path.dirname(repository_path), 'sql')

    def _build_db_request(self, sql_file_name: str, args: dict = None):
        return DatabaseRequest(
            sql=get_sql_from_file(path.join(self.sql_dir, sql_file_name)),
            args=args
        )
