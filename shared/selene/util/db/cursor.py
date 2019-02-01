"""Utility code for interacting with a database.

Example Usage:
    from util.db import get_sql_from_file, mycroft_db_ro
    sql = get_sql_from_file(<fully qualified path to .sql file>)
    query_result = mycroft_db_ro.execute_sql(sql)
"""

from dataclasses import dataclass, field
from logging import getLogger
from os import path

_log = getLogger(__package__)


class DBConnectionError(Exception):
    pass


def get_sql_from_file(file_path: str) -> str:
    """
    Read a .sql file and return its contents as a string.

    All the SQL to access relational databases will be written in .sql files
    :param file_path: absolute file system of the .sql file.
    :return: raw SQL for use in a database interface, such as psycopg
    """
    with open(path.join(file_path)) as sql_file:
        raw_sql = sql_file.read()

    print(raw_sql)
    return raw_sql


@dataclass
class DatabaseRequest(object):
    file_path: str
    args: dict = field(default=None)


class Cursor(object):
    def __init__(self, db):
        self.db = db

    def _fetch(self, db_request: DatabaseRequest, singleton=False):
        """
        Fetch all or one row from the database.
        :param db_request: parameters used to determine how to fetch the data
        :return: the query results; will be a results object if a singleton select
            was issued, a list of results objects otherwise.
        """
        sql = get_sql_from_file(db_request.file_path)
        with self.db.cursor() as cursor:
            _log.debug(cursor.mogrify(sql, db_request.args))
            cursor.execute(sql, db_request.args)
            if singleton:
                execution_result = cursor.fetchone()
            else:
                execution_result = cursor.fetchall()

            _log.debug('query returned {} rows'.format(cursor.rowcount))

        return execution_result

    def select_one(self, db_request: DatabaseRequest):
        """
        Fetch a single row from the database.

        :param db_request: parameters used to determine how to fetch the data
        :return: a single results object
        """
        return self._fetch(db_request, singleton=True)

    def select_all(self, db_request: DatabaseRequest):
        """
        Fetch all rows resulting from the database request.

        :param db_request: parameters used to determine how to fetch the data
        :return: a single results object
        """
        return self._fetch(db_request)

    def _execute(self, db_request: DatabaseRequest):
        """
        Fetch all or one row from the database.
        :param db_request: parameters used to determine how to fetch the data
        :return: the query results; will be a results object if a singleton select
            was issued, a list of results objects otherwise.
        """
        sql = get_sql_from_file(db_request.file_path)
        with self.db.cursor() as cursor:
            _log.debug(cursor.mogrify(sql, db_request.args))
            cursor.execute(sql, db_request.args)
            _log.debug(str(cursor.rowcount) + 'rows affected')

    def delete(self, db_request: DatabaseRequest):
        self._execute(db_request)

    def insert(self, db_request: DatabaseRequest):
        self._execute(db_request)

    def update(self, db_request: DatabaseRequest):
        self._execute(db_request)
