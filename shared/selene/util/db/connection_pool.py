"""Postgres database connection pooling helpers"""

from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger

from psycopg2.pool import ThreadedConnectionPool

from .connection import DatabaseConnectConfig

_log = getLogger(__package__)


@dataclass
class DatabaseConnectionPoolConfig(DatabaseConnectConfig):
    max_connections: int


def init_db_connection_pool(
        connection_config: DatabaseConnectionPoolConfig,
) -> ThreadedConnectionPool:
    """
    Allocate a pool of database connections for an application

    Connecting to a database can be a costly operation for stateless
    applications that jump in and out of a database frequently,
    like a REST APIs. To combat this, a connection pool provides a set of
    persistent connections that preclude these applications from constantly
    connecting and disconnecting from the database.

    :param connection_config: data needed to establish a connection
    :return: a pool of database connections to be used by the application
    """
    log_msg = (
        'Allocating a pool of connections to the {db_name} database with '
        'a maximum of {max_connections} connections.'
    )
    _log.info(log_msg.format(
        db_name=connection_config.db_name,
        max_connections=connection_config.max_connections)
    )
    return ThreadedConnectionPool(
        minconn=1,
        maxconn=connection_config.max_connections,
        database=connection_config.db_name,
        user=connection_config.user,
        password=connection_config.password,
        host=connection_config.host,
        port=connection_config.port
    )


@contextmanager
def get_db_connection(connection_pool):
    db_connection = None
    try:
        db_connection = connection_pool.getconn()
        yield db_connection
    finally:
        if db_connection is not None:
            connection_pool.putconn(db_connection)
