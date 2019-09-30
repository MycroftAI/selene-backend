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

"""Tools for executing sql within a transaction."""
from functools import wraps


def use_transaction(func):
    """Execute all sql statements within the wrapped function in a transaction

    This is a decorator that assumes the function it is wrapping is a method
    of a class with a "db" attribute that is a psycopg connection object.

    :param func: function being decorated
    :return: decorated function
    """
    @wraps(func)
    def execute_in_transaction(*args, **kwargs):
        instance = args[0]
        return_value = None
        if hasattr(instance, "db"):
            prev_autocommit = instance.db.autocommit
            instance.db.autocommit = False
            try:
                return_value = func(*args, **kwargs)
            except:
                instance.db.rollback()
                raise
            else:
                instance.db.commit()
            instance.db.autocommit = prev_autocommit

        return return_value

    return execute_in_transaction
