"""Utility code for interacting with a database.

Example Usage:
    from util.db import get_sql_from_file, mycroft_db_ro
    sql = get_sql_from_file(<fully qualified path to .sql file>)
    query_result = mycroft_db_ro.execute_sql(sql)
"""

from dataclasses import dataclass
from logging import getLogger
from os import path
from os import environ

from psycopg2 import connect
from psycopg2.extras import RealDictCursor

_log = getLogger(__package__)

DB_HOST = environ['DB_HOST']


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


def _connect_to_mycroft_db(db_user):
    """
    Return a connection to the mycroft database for the specified user.

    :param db_user: name of user to pass to connection request
    :return: database connection
    """
    db = connect(
        host=DB_HOST,
        dbname='mycroft',
        user=db_user,
        cursor_factory=RealDictCursor
    )
    db.autocommit = True

    return db


def get_view_connection():
    """Return a connection to the mycroft database for the view user."""
    return _connect_to_mycroft_db(db_user='selene_view')


def get_crud_connection():
    """Return a connection to the mycroft database for the CRUD user."""
    return _connect_to_mycroft_db(db_user='selene_crud')


@dataclass
class DatabaseQuery(object):
    file_path: str
    args: dict
    singleton: bool


def fetch(db, db_query: DatabaseQuery):
    """
    Fetch all or one row from the database.
    :param db: connection to the mycroft database.
    :param db_query: parameters used to determine how to fetch the data
    :return: the query results; will be a results object if a singleton select
        was issued, a list of results objects otherwise.
    """
    sql = get_sql_from_file(db_query.file_path)
    print(db_query.file_path)
    with db.cursor() as cursor:
        _log.debug(cursor.mogrify(sql, db_query.args))
        cursor.execute(sql, db_query.args)
        if db_query.singleton:
            execution_result = cursor.fetchone()
        else:
            execution_result = cursor.fetchall()
            _log.debug('query returned {} rows'.format(cursor.rowcount))

    return execution_result
