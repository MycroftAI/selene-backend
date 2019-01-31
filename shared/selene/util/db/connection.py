"""Utility code for interacting with a database.

Example Usage:
    from util.db import get_sql_from_file, mycroft_db_ro
    sql = get_sql_from_file(<fully qualified path to .sql file>)
    query_result = mycroft_db_ro.execute_sql(sql)
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
from logging import getLogger

from psycopg2 import connect
from psycopg2.extras import RealDictCursor

_log = getLogger(__package__)


class DBConnectionError(Exception):
    pass


@dataclass
class DatabaseConnectConfig(object):
    host: str
    db_name: str
    user: str
    password: str
    port: int = field(default=5432)


@contextmanager
def connect_to_db(connection_config: DatabaseConnectConfig):
    """
    Return a connection to the mycroft database for the specified user.

    :param connection_config: data needed to establish a connection
    :return: database connection
    """
    db = None
    log_msg = 'establishing connection to the {db_name} database'
    _log.info(log_msg.format(db_name=connection_config.db_name))
    try:
        db = connect(
            host=connection_config.host,
            dbname=connection_config.db_name,
            user=connection_config.user,
            cursor_factory=RealDictCursor
        )
        db.autocommit = True
        yield db
    finally:
        if db is not None:
            db.close()
