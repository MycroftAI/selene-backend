# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Postgres database connection pooling helpers"""

from contextlib import contextmanager
from logging import getLogger

from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from .connection import DatabaseConnectionConfig

_log = getLogger(__name__)


def allocate_db_connection_pool(
    connection_config: DatabaseConnectionConfig, max_connections: int = 20
) -> ThreadedConnectionPool:
    """
    Allocate a pool of database connections for an application

    Connecting to a database can be a costly operation for stateless
    applications that jump in and out of a database frequently,
    like a REST APIs. To combat this, a connection pool provides a set of
    persistent connections that preclude these applications from constantly
    connecting and disconnecting from the database.

    :param connection_config: data needed to establish a connection
    :param max_connections: maximum connections allocated to the application
    :return: a pool of database connections to be used by the application
    """
    log_msg = (
        "Allocating a pool of connections to the {db_name} database with "
        "a maximum of {max_connections} connections."
    )
    _log.info(
        log_msg.format(
            db_name=connection_config.db_name, max_connections=max_connections
        )
    )
    return ThreadedConnectionPool(
        minconn=1,
        maxconn=max_connections,
        database=connection_config.db_name,
        user=connection_config.user,
        password=connection_config.password,
        host=connection_config.host,
        port=connection_config.port,
        cursor_factory=RealDictCursor,
    )


@contextmanager
def get_db_connection(connection_pool, autocommit=True):
    """Obtain a database connection from a pool and release it when finished

    :param connection_pool: pool of connections used by the applications
    :param autocommit: indicates if transactions should commit automatically
    :return: context object containing a database connection from the pool
    """
    db_connection = None
    try:
        db_connection = connection_pool.getconn()
        db_connection.autocommit = autocommit
        yield db_connection
    finally:
        # return the db connection to the pool when exiting the context
        # manager's scope
        if db_connection is not None:
            connection_pool.putconn(db_connection)


def get_db_connection_from_pool(connection_pool, autocommit=True):
    """Obtain a database connection from a pool and release it when finished

    :param connection_pool: pool of connections used by the applications
    :param autocommit: indicates if transactions should commit automatically
    :return: context object containing a database connection from the pool
    """
    db_connection = connection_pool.getconn()
    db_connection.autocommit = autocommit

    return db_connection


def return_db_connection_to_pool(connection_pool, connection):
    """Returns a connection to the connection pool when it is no longer needed."""
    connection_pool.putconn(connection)
