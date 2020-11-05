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

"""Utility code for interacting with a database.

Example Usage:
    from util.db import get_sql_from_file, mycroft_db_ro
    sql = get_sql_from_file(<fully qualified path to .sql file>)
    query_result = mycroft_db_ro.execute_sql(sql)
"""

from dataclasses import dataclass, field, InitVar
from logging import getLogger

from psycopg2 import connect
from psycopg2.extras import RealDictCursor, NamedTupleCursor
from psycopg2.extensions import cursor

_log = getLogger(__package__)


class DBConnectionError(Exception):
    pass


@dataclass
class DatabaseConnectionConfig(object):
    """attributes required to connect to a Postgres database"""
    host: str
    db_name: str
    user: str
    password: str
    port: int = field(default=5432)
    sslmode: str = None
    autocommit: str = True
    cursor_factory = RealDictCursor
    use_namedtuple_cursor: InitVar[bool] = False

    def __post_init__(self, use_namedtuple_cursor: bool):
        """
        Initialize the namedtuple.

        Args:
            self: (todo): write your description
            use_namedtuple_cursor: (str): write your description
        """
        if use_namedtuple_cursor:
            self.cursor_factory = NamedTupleCursor


def connect_to_db(connection_config: DatabaseConnectionConfig):
    """
    Return a connection to the mycroft database for the specified user.

    Use this function when connecting to a database in an application that
    does not benefit from connection pooling (e.g. a batch script or a
    python notebook)

    :param connection_config: data needed to establish a connection
    :return: database connection
    """
    log_msg = 'establishing connection to the {db_name} database'
    _log.info(log_msg.format(db_name=connection_config.db_name))
    db = connect(
        host=connection_config.host,
        dbname=connection_config.db_name,
        user=connection_config.user,
        password=connection_config.password,
        port=connection_config.port,
        cursor_factory=connection_config.cursor_factory,
        sslmode=connection_config.sslmode
    )
    db.autocommit = connection_config.autocommit

    return db
