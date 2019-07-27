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

"""Base class that all data repository classes should inherit from

This class contains boilerplate code that is necessary for all repository
classes such as building a database request and a cursor object.
"""
from os import path
from typing import List

from selene.util.db import (
    Cursor,
    DatabaseRequest,
    DatabaseBatchRequest,
    get_sql_from_file
)


def _instantiate_dataclass(dataclass, db_result):
    """Build a dataclass instance using a row of a query result.

    Depending on the cursor factory assigned to the database connection, the
    keyword arguments used to instantiate a dataclass may need to be converted
    to a dictionary first.
    """
    try:
        dataclass_instance = dataclass(**db_result)
    except TypeError:
        dataclass_instance = dataclass(**db_result._asdict())

    return dataclass_instance


class RepositoryBase(object):
    def __init__(self, db, repository_path):
        self.db = db
        self.cursor = Cursor(db)
        self.sql_dir = path.join(path.dirname(repository_path), 'sql')

    def _build_db_request(
            self, sql_file_name: str, args: dict = None, sql_vars: dict = None
    ):
        """Build a DatabaseRequest object containing a query and args"""
        sql = get_sql_from_file(path.join(self.sql_dir, sql_file_name))
        if sql_vars is not None:
            sql = sql.format(**sql_vars)

        return DatabaseRequest(sql, args)

    def _build_db_batch_request(self, sql_file_name: str, args: List[dict]):
        """Build a DatabaseBatchRequest object containing a query and args"""
        return DatabaseBatchRequest(
            sql=get_sql_from_file(path.join(self.sql_dir, sql_file_name)),
            args=args
        )

    def _select_one_into_dataclass(self, dataclass, sql_file_name, args=None):
        """Execute a query and instantiate the dataclass with its results."""
        db_request = self._build_db_request(sql_file_name, args)
        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            dataclass_instance = None
        else:
            dataclass_instance = _instantiate_dataclass(dataclass, db_result)

        return dataclass_instance

    def _select_all_into_dataclass(self, dataclass, sql_file_name, args=None):
        """Execute a query and instantiate the dataclass with its results."""
        db_request = self._build_db_request(sql_file_name, args)
        db_result = self.cursor.select_all(db_request)

        return [_instantiate_dataclass(dataclass, row) for row in db_result]
