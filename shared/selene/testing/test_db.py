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

from psycopg2 import connect

connection_config = dict(
    host='127.0.0.1',
    dbname='postgres',
    user='mycroft',
    password='holmes'
)


def create_test_db():
    """
    Create database.

    Args:
    """
    db = connect(**connection_config)
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(
        'CREATE DATABASE '
        '   mycroft_test '
        'WITH TEMPLATE '
        '    mycroft_template '
        'OWNER '
        '    mycroft;'
    )


def drop_test_db():
    """
    Drop the database.

    Args:
    """
    db = connect(**connection_config)
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(
        'SELECT pg_terminate_backend(pid) '
        'FROM pg_stat_activity '
        'WHERE datname = \'mycroft_test\';'
    )
    cursor.execute('DROP DATABASE mycroft_test')
