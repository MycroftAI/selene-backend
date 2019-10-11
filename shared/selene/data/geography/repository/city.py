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

from ..entity.city import City, GeographicLocation
from ...repository_base import RepositoryBase


class CityRepository(RepositoryBase):
    def __init__(self, db):
        super(CityRepository, self).__init__(db, __file__)

    def get_cities_by_region(self, region_id):
        db_request = self._build_db_request(
            sql_file_name='get_cities_by_region.sql',
            args=dict(region_id=region_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [City(**row) for row in db_result]

    def get_geographic_location_by_city(self, possible_city_names: list):
        """Return a list of all cities matching the list of possibilities"""
        city_names = [nm.lower() for nm in possible_city_names]
        return self._select_all_into_dataclass(
            GeographicLocation,
            sql_file_name='get_geographic_location_by_city.sql',
            args=dict(possible_city_names=tuple(city_names))

        )

    def get_biggest_city_in_region(self, region_name):
        """Return the geolocation of the most populous city in a region."""
        return self._select_one_into_dataclass(
            GeographicLocation,
            sql_file_name='get_biggest_city_in_region.sql',
            args=dict(region=region_name.lower())
        )

    def get_biggest_city_in_country(self, country_name):
        """Return the geolocation of the most populous city in a country."""
        return self._select_one_into_dataclass(
            GeographicLocation,
            sql_file_name='get_biggest_city_in_country.sql',
            args=dict(country=country_name.lower())
        )
