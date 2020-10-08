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

from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import CityRepository


class CityEndpoint(SeleneEndpoint):
    def get(self):
        region_id = self.request.args["region"]
        city_repository = CityRepository(self.db)
        cities = city_repository.get_cities_by_region(region_id=region_id)

        for city in cities:
            city.longitude = float(city.longitude)
            city.latitude = float(city.latitude)

        return cities, HTTPStatus.OK
