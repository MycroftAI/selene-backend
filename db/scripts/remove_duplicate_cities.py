# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
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
"""Short script to delete duplicate rows from the geography.city table"""
from os import environ
from pathlib import Path

from selene.util.db import (
    connect_to_db,
    Cursor,
    DatabaseConnectionConfig,
    DatabaseRequest,
    get_sql_from_file,
)

MYCROFT_DB_DIR = environ.get("DB_DIR", "/opt/selene/selene-backend/db/mycroft")


def get_cursor():
    """Get a cursor object for executing SQL against the DB"""
    db_connection_config = DatabaseConnectionConfig(
        host=environ["DB_HOST"],
        db_name=environ["DB_NAME"],
        password=environ["DB_PASSWORD"],
        port=environ.get("DB_PORT", 5432),
        user=environ["DB_USER"],
        sslmode=environ.get("DB_SSLMODE"),
    )
    db = connect_to_db(db_connection_config)
    cursor = Cursor(db)

    return cursor


def get_duplicate_cities(cursor):
    """Get a list of the cities that appear multiple times in the city table."""
    geography_dir = Path(MYCROFT_DB_DIR).joinpath("geography_schema")
    sql = get_sql_from_file(str(geography_dir.joinpath("get_duplicated_cities.sql")))
    request = DatabaseRequest(sql)
    result = cursor.select_all(request)
    print("Removing duplicate cities from the geography.city table")
    print(f"found {len(result)} duplicated cities")

    return result


def get_device_geographies(cursor, city):
    """Get any device.geography rows that use one of the duplicated cities."""
    device_dir = Path(MYCROFT_DB_DIR).joinpath("device_schema")
    sql = get_sql_from_file(
        str(device_dir.joinpath("get_device_geographies_for_city.sql"))
    )
    args = dict(city_ids=tuple(city["city_ids"]))
    request = DatabaseRequest(sql, args)
    result = cursor.select_all(request)
    if result:
        print(
            f"found {len(result)} device geographies for city: {city['city_name']}; "
            f"region: {city['region_name']}; country: {city['country_name']}"
        )

    return result


def get_account_defaults(cursor, city):
    """Get any device.account_default rows that use one of the duplicated cities."""
    device_dir = Path(MYCROFT_DB_DIR).joinpath("device_schema")
    sql = get_sql_from_file(
        str(device_dir.joinpath("get_device_defaults_for_city.sql"))
    )
    args = dict(city_ids=tuple(city["city_ids"]))
    request = DatabaseRequest(sql, args)
    result = cursor.select_all(request)
    if result:
        print(f"found {len(result)} device defaults for {city['city_name']}")

    return result


def check_device_geography_for_dup_cities(cursor, duplicate_cities):
    """Checks for duplicated cities on the device.geography table.

    In theory this should not find any matches as the GUI breaks when a city with
    duplicates is chosen.  No logic to deal with this scenario is in here yet, but will
    be added if the assumption is proven wrong.
    """
    device_geographies_found = False
    for city in duplicate_cities:
        device_geographies = get_device_geographies(cursor, city)
        if device_geographies:
            device_geographies_found = True
    if not device_geographies_found:
        print("there are no devices assigned to duplicated city")

    return device_geographies_found


def check_account_defaults_for_dup_cities(cursor, duplicate_cities):
    """Checks for duplicated cities on the device.account_default table.

    In theory this should not find any matches as the GUI breaks when a city with
    duplicates is chosen.  No logic to deal with this scenario is in here yet, but will
    be added if the assumption is proven wrong.
    """
    account_defaults_found = False
    for city in duplicate_cities:
        account_defaults = get_account_defaults(cursor, city)
        if account_defaults:
            account_defaults_found = True
    if not account_defaults_found:
        print("there are no account defaults using a duplicated city")

    return account_defaults_found


def delete_duplicates(cursor, city, used_cities):
    """Once all the checks are done, we can delete the rows from the database.

    Remove the first ID from the list so that one of the rows remains.
    """
    deleted_rows = 0
    geography_dir = Path(MYCROFT_DB_DIR).joinpath("geography_schema")
    sql = get_sql_from_file(str(geography_dir.joinpath("delete_duplicate_cities.sql")))
    if used_cities:
        sql += " and id not in %(used_cities)s"
        args = dict(
            city_ids=tuple(city["city_ids"]),
            max_population=city["max_population"],
            used_cities=tuple(used_cities),
        )
    else:
        args = dict(
            city_ids=tuple(city["city_ids"]), max_population=city["max_population"],
        )
    request = DatabaseRequest(sql, args)
    result = cursor.delete(request)
    deleted_rows += result

    print(f"Deleted {deleted_rows} from the geography.city table")


def main():
    """Make it so."""
    cursor = get_cursor()
    duplicate_cities = get_duplicate_cities(cursor)
    account_defaults_found = check_account_defaults_for_dup_cities(
        cursor, duplicate_cities
    )
    if account_defaults_found:
        print("Great, now you need to write more code!")
    else:
        for city in duplicate_cities:
            device_geographies = get_device_geographies(cursor, city)
            if not device_geographies:
                delete_duplicates(cursor, city, [])
            else:
                print(device_geographies)
                used_cities = [geo["city_id"] for geo in device_geographies]
                delete_duplicates(cursor, city, used_cities)
                break


if __name__ == "__main__":
    main()
